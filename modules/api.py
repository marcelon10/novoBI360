import strawberry, os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, text
import urllib.parse

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
        
@strawberry.type
class Captura:
    date: str
    totalCount: int
    totalAuto: int
    documentType: str
    
@strawberry.type
class Query:
    @strawberry.field
    def get_captura(self) -> list[Captura]:
        query = text("""
        select
        	date_trunc('month', process_created_at) as mes,
            count(*) as total,
            sum(case 
                when captura_status in ('Email', 'Automático') then 1 else 0 
            end) as total_automatico,
        	document_type
        from
        	mview_process_fact mpf
        group by
        	mes,
        	document_type
        order by
        	mes
        """)
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()
            return [Captura(date=r[0], totalCount=r[1], totalAuto=r[2], documentType=r[3]) for r in rows]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)