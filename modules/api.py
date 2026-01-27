import strawberry, os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, text
import urllib.parse
from typing import Optional, List

# 1. Your raw credentials
user = "analytics"
password = os.getenv('PWD_INTERNAL')
host = "localhost"
port = "15432"
db_name = "dw_aegea"

# 2. URL-encode the password (and the user, just in case)
safe_user = urllib.parse.quote_plus(user)
safe_password = urllib.parse.quote_plus(password)

# 3. Construct the connection string
# It will look like: postgresql://user:Xdh%40t5%25%21@localhost:5432/dbname
DATABASE_URL = f"postgresql://{safe_user}:{safe_password}@{host}:{port}/{db_name}"
# 1. Database Connection
engine = create_engine(DATABASE_URL) # Replace with your Postgres/SQL string
        
@strawberry.input
class FilterInput:
    field: str
    value: str
    operator: str = "eq" # eq, gte, lte, in        
        
@strawberry.type
class Captura:
    date: str
    totalCount: int
    totalAuto: int
    documentType: str
    
@strawberry.type
class Query:
    @strawberry.field
    def get_captura(self, grain: str = "month", filters: Optional[List[FilterInput]] = None) -> List[Captura]:
        # O SQL usa o parâmetro 'grain' diretamente no date_trunc
        sql_base = f"""
        SELECT
            date_trunc('{grain}', process_created_at)::text as {grain},
            count(*) as total,
            sum(case when captura_status in ('Email', 'Automático') then 1 else 0 end) as total_automatico,
            document_type
        FROM mview_process_fact mpf
        WHERE 1=1
        """
        
        params = {}
        filter_sql = ""

        # 2. Build the WHERE clause
        if filters:
            for i, f in enumerate(filters):
                param_name = f"val_{i}"
                if f.operator == "gte":
                    filter_sql += f" AND {f.field} >= :{param_name}"
                elif f.operator == "lte":
                    filter_sql += f" AND {f.field} <= :{param_name}"
                elif f.operator == "in":
                    filter_sql += f" AND {f.field} IN ({f.value})"
                else:
                    filter_sql += f" AND {f.field} = :{param_name}"
                params[param_name] = f.value

        # 3. Add GROUP BY and ORDER BY at the very end
        full_query = sql_base + filter_sql + " GROUP BY 1, document_type ORDER BY 1"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            # Note: Added documentType to the constructor to match your Captura class
            return [Captura(date=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)