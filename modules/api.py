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
db_name = "analytics"

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
class CapturaFornecedores:
    supplierCnpj: str
    totalCount: int
    totalAuto: int
    documentType: str

@strawberry.type
class CapturaCidades:
    currency: str
    totalCount: int
    totalAuto: int
    documentType: str
    
@strawberry.type
class CapturaAnalitica:
    id: int
    supplierCnpj: str
    issueDate: str
    provider: str
    totalValue: float 
    documentType: str 

@strawberry.type
class Query:
    @strawberry.field
    def get_captura(self, grain: str = "month", customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[Captura]:
        # O SQL usa o parâmetro 'grain' diretamente no date_trunc
        sql_base = f"""
        SELECT
            date_trunc('{grain}', process_created_at)::text as {grain},
            sum(total_notas) as total_count,
            sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
            document_type
        FROM mview_teste_bi_captura
        WHERE c_id = '{customer}'
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

    @strawberry.field
    def get_captura_fornecedores(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[CapturaFornecedores]:
        sql_base = f"""
        SELECT
            supplier_cnpj,
            sum(total_notas) as total_count,
            sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
            document_type
        FROM mview_bi_captura_fornecedores
        WHERE c_id = '{customer}'
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
        full_query = sql_base + filter_sql + " GROUP BY supplier_cnpj, document_type ORDER BY total_count DESC LIMIT 10"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [CapturaFornecedores(supplierCnpj=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]
        
    
    @strawberry.field
    def get_captura_cidades(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[CapturaCidades]:
        sql_base = f"""
        SELECT
            coalesce(currency, 'Sem Cidade') as currency,
            sum(total_notas) as total_count,
            sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
            document_type
        FROM mview_bi_captura_cidades
        WHERE c_id = '{customer}'
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
        full_query = sql_base + filter_sql + " GROUP BY currency, document_type ORDER BY total_count DESC LIMIT 10"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [CapturaCidades(currency=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]

    @strawberry.field
    def get_captura_analitico(self, customer: str = None, limit: int = 50, offset: int = 0, filters: Optional[List[FilterInput]] = None) -> List[CapturaAnalitica]:
        
        sql_base = f"""
            SELECT id, supplier_cnpj, issue_date, provider, total_value, type as document_type
            FROM tax_documents
            WHERE c_id = '{customer}'
        """
        
        params = {}
        filter_sql = ""

        # 2. Build the WHERE clause
        if filters:
            for i, f in enumerate(filters):
                
                if f.field == 'process_created_at':
                    f.field = 'created_at'
                    
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
        full_query = sql_base + filter_sql + f" ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}"
        
        print(full_query)
        print(params)

        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [CapturaAnalitica(id=int(r[0]), supplierCnpj=r[1], issueDate=r[2], 
                                     provider=r[3], totalValue=r[4], documentType=r[5]) for r in rows]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)