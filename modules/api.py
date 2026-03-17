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
class Divergencia:
    date: str
    totalCount: int
    totalComDivergencia: int
    documentType: str
    
@strawberry.type
class DivergenciaFornecedores:
    supplierCnpj: str
    totalCount: int

@strawberry.type
class DivergenciaTipo:
    nomeDivergencia: str
    totalCount: int
    
@strawberry.type
class DivergenciaAnalitica:
    id: int
    nomeDivergencia: str
    idNota: int
    targetValue: str
    fieldValue: str
    createdAt: str

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
        FROM mview_process_{customer}
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

    @strawberry.field
    def get_captura_fornecedores(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[CapturaFornecedores]:
        sql_base = f"""
        SELECT
            supplier_cnpj,
            sum(total_notas) as total_count,
            sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
            document_type
        FROM mview_process_{customer}
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
            coalesce(customer_cnpj, 'Sem Cidade') as currency,
            sum(total_notas) as total_count,
            sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
            document_type
        FROM mview_process_{customer}
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
            WHERE c_id = '{customer}_prod'
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

    @strawberry.field
    def get_filter_options(self, customer: str) -> strawberry.scalars.JSON:
        # 1. Query para Fluxos (Usando a MView do cliente)
        # Note: Removi o WHERE c_id porque a mview_process_{customer} já é específica
        query_fluxos = f"SELECT DISTINCT process_name FROM mview_process_{customer} WHERE process_name IS NOT NULL ORDER BY 1"
        
        # 2. Query para Fornecedores
        query_fornecedores = f"SELECT DISTINCT supplier_cnpj FROM mview_process_{customer} WHERE supplier_cnpj IS NOT NULL ORDER BY 1"
        
        # 3. Query para Tomadores
        query_tomadores = f"SELECT DISTINCT customer_cnpj FROM mview_process_{customer} WHERE customer_cnpj IS NOT NULL ORDER BY 1"

        options = {
            "fluxos": [],
            "fornecedores": [],
            "tomadores": []
        }

        with engine.connect() as conn:
            try:
                # Executando direto, já que o customer está injetado no nome da tabela via f-string
                options["fluxos"] = [r[0] for r in conn.execute(text(query_fluxos)).fetchall()]
                options["fornecedores"] = [r[0] for r in conn.execute(text(query_fornecedores)).fetchall()]
                options["tomadores"] = [r[0] for r in conn.execute(text(query_tomadores)).fetchall()]
            except Exception as e:
                print(f"Erro ao buscar opções SQL: {e}")
                
        return options
    
    @strawberry.field
    def get_divergencia(self, grain: str = "month", customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[Divergencia]:
        # O SQL usa o parâmetro 'grain' diretamente no date_trunc
        sql_base = f"""
        SELECT
            date_trunc('{grain}', process_created_at)::text as {grain},
            sum(total_notas) as total_count,
            sum(case when divergence_flag = 'Com Divergência' then total_notas else 0 end) as total_com_divergencia,
            document_type
        FROM mview_process_{customer}
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
        full_query = sql_base + filter_sql + " GROUP BY 1, 4 ORDER BY 1"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            # Note: Added documentType to the constructor to match your Captura class
            return [Divergencia(date=r[0], totalCount=r[1], totalComDivergencia=int(r[2]), documentType=r[3]) for r in rows]

    @strawberry.field
    def get_divergencia_fornecedores(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaFornecedores]:
        sql_base = f"""
        SELECT
            supplier_cnpj,
            sum(total_divergencia) as total_count
        FROM mview_divergence_{customer}
        WHERE 1=1
        """
        
        params = {}
        filter_sql = ""

        # 2. Build the WHERE clause
        if filters:
            for i, f in enumerate(filters):
                
                if f.field == 'process_created_at':
                    f.field = 'divergence_created_at'                
                
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
        full_query = sql_base + filter_sql + " GROUP BY supplier_cnpj ORDER BY total_count DESC LIMIT 10"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [DivergenciaFornecedores(supplierCnpj=r[0], totalCount=r[1]) for r in rows]
        
    
    @strawberry.field
    def get_divergencia_tipo(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaTipo]:
        sql_base = f"""
        SELECT
            nome_divergencia,
            sum(total_divergencia) as total_count
        FROM mview_divergence_{customer}
        WHERE 1=1
        """
        
        params = {}
        filter_sql = ""

        # 2. Build the WHERE clause
        if filters:
            for i, f in enumerate(filters):
                
                if f.field == 'process_created_at':
                    f.field = 'divergence_created_at'                
                
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
        full_query = sql_base + filter_sql + " GROUP BY nome_divergencia ORDER BY total_count DESC LIMIT 10"
        
        print(full_query)
        print(params)
        
        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [DivergenciaTipo(nomeDivergencia=r[0], totalCount=r[1]) for r in rows]

    @strawberry.field
    def get_divergencia_analitico(self, customer: str = None, limit: int = 50, offset: int = 0, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaAnalitica]:
        
        sql_base = f"""
            select id as id_divergencia, coalesce(validation_error_name, 'Sem Nome') as nome_divergencia,
            coalesce(associated_to_id, 0) as id_nota, 
            coalesce(validation_target_value, 'Sem Valor') as validation_target_value,
            coalesce(validation_data_field_value, 'Sem Valor') as validation_data_field_value,
            validation_record_created_at
            from divergences
            WHERE c_id = '{customer}_prod'
        """
        
        params = {}
        filter_sql = ""

        # 2. Build the WHERE clause
        if filters:
            for i, f in enumerate(filters):
                
                if f.field == 'process_created_at':
                    f.field = 'validation_record_created_at'
                    
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
        full_query = sql_base + filter_sql + f" ORDER BY validation_record_created_at DESC LIMIT {limit} OFFSET {offset}"
        
        print(full_query)
        print(params)

        with engine.connect() as conn:
            rows = conn.execute(text(full_query), params).fetchall()
            return [DivergenciaAnalitica(id=int(r[0]), nomeDivergencia=r[1], idNota=r[2], 
                                     targetValue=r[3], fieldValue=r[4], createdAt=r[5]) for r in rows]                


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)