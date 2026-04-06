import asyncio
import strawberry, os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, text
import urllib.parse
from typing import Optional, List

# 1. Your raw credentials
user = os.getenv('USER_MULTI_TENANCY')
password = os.getenv('PWD_MULTI_TENANCY')
host = os.getenv('HOST_MULTI_TENANCY')
port = "5432"
db_name = "dasa_prod_multi_tenancy"

# 2. URL-encode the password (and the user, just in case)
safe_user = urllib.parse.quote_plus(user)
safe_password = urllib.parse.quote_plus(password)

# 3. Construct the connection string
DATABASE_URL = f"postgresql://{safe_user}:{safe_password}@{host}:{port}/{db_name}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # keep 10 connections open permanently
    max_overflow=20,     # allow up to 20 extra connections under burst load
    pool_pre_ping=True,  # test connections before use (drops stale ones)
    pool_timeout=30,     # wait up to 30s for a connection before raising
    pool_recycle=1800,   # recycle connections every 30min to avoid timeouts
)


def build_filter_sql(filters):
    """Returns (filter_sql, params) from a list of FilterInput."""
    filter_sql = ""
    params = {}
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
    return filter_sql, params


@strawberry.input
class FilterInput:
    field: str
    value: str
    operator: str = "eq"  # eq, gte, lte, in

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
class NotasAberto:
    date: str
    totalEmAberto: int
    totalEmAbertoHumanas: int

@strawberry.type
class NotasAbertoUsuario:
    userName: str
    totalCount: int

@strawberry.type
class NotasAbertoTarefa:
    nomeTarefa: str
    totalCount: int

@strawberry.type
class NotasAbertoAnalitica:
    id: int
    createdAt: str
    nomeTarefa: str
    userName: str


@strawberry.type
class Query:

    @strawberry.field
    async def get_captura(self, grain: str = "month", customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[Captura]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                date_trunc('{grain}', process_created_at)::text as {grain},
                sum(total_notas) as total_count,
                sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
                document_type
            FROM mview_process_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY 1, document_type ORDER BY 1"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [Captura(date=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_captura_fornecedores(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[CapturaFornecedores]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                coalesce(supplier_cnpj, 'N/A') as supplier_cnpj,
                sum(total_notas) as total_count,
                sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
                document_type
            FROM mview_process_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY supplier_cnpj, document_type ORDER BY total_count DESC LIMIT 10"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [CapturaFornecedores(supplierCnpj=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_captura_cidades(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[CapturaCidades]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                coalesce(customer_cnpj, 'Sem Cidade') as currency,
                sum(total_notas) as total_count,
                sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
                document_type
            FROM mview_process_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY currency, document_type ORDER BY total_count DESC LIMIT 10"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [CapturaCidades(currency=r[0], totalCount=r[1], totalAuto=int(r[2]), documentType=r[3]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_captura_analitico(self, customer: str = None, limit: int = 50, offset: int = 0, filters: Optional[List[FilterInput]] = None) -> List[CapturaAnalitica]:
        mapped = []
        if filters:
            for f in filters:
                if f.field == 'process_created_at':
                    f.field = 'created_at'
                mapped.append(f)
        filter_sql, params = build_filter_sql(mapped)
        full_query = f"""
            SELECT id, supplier_cnpj, issue_date, provider, total_value, type as document_type
            FROM tax_documents
            WHERE c_id = '{customer}_prod'
        """ + filter_sql + f" ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [CapturaAnalitica(id=int(r[0]), supplierCnpj=r[1], issueDate=r[2],
                                         provider=r[3], totalValue=r[4], documentType=r[5]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_filter_options(self, customer: str) -> strawberry.scalars.JSON:
        queries = {
            "fluxos":       f"SELECT DISTINCT process_name  FROM mview_process_{customer} WHERE process_name  IS NOT NULL ORDER BY 1",
            "fornecedores": f"SELECT DISTINCT supplier_cnpj FROM mview_process_{customer} WHERE supplier_cnpj IS NOT NULL ORDER BY 1",
            "tomadores":    f"SELECT DISTINCT customer_cnpj FROM mview_process_{customer} WHERE customer_cnpj IS NOT NULL ORDER BY 1",
        }

        async def run_one(key, sql):
            def _query():
                with engine.connect() as conn:
                    try:
                        return [r[0] for r in conn.execute(text(sql)).fetchall()]
                    except Exception as e:
                        print(f"Erro ao buscar opções SQL ({key}): {e}")
                        return []
            return key, await asyncio.to_thread(_query)

        results = await asyncio.gather(*[run_one(k, sql) for k, sql in queries.items()])
        return {k: v for k, v in results}

    @strawberry.field
    async def get_divergencia(self, grain: str = "month", customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[Divergencia]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                date_trunc('{grain}', process_created_at)::text as {grain},
                sum(total_notas) as total_count,
                sum(case when divergence_flag = 'Com Divergência' then total_notas else 0 end) as total_com_divergencia,
                document_type
            FROM mview_process_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY 1, 4 ORDER BY 1"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [Divergencia(date=r[0], totalCount=r[1], totalComDivergencia=int(r[2]), documentType=r[3]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_divergencia_fornecedores(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaFornecedores]:
        mapped = []
        if filters:
            for f in filters:
                if f.field == 'process_created_at':
                    f.field = 'divergence_created_at'
                mapped.append(f)
        filter_sql, params = build_filter_sql(mapped)
        full_query = f"""
            SELECT
                supplier_cnpj,
                sum(total_divergencia) as total_count
            FROM mview_divergence_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY supplier_cnpj ORDER BY total_count DESC LIMIT 10"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [DivergenciaFornecedores(supplierCnpj=r[0], totalCount=r[1]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_divergencia_tipo(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaTipo]:
        mapped = []
        if filters:
            for f in filters:
                if f.field == 'process_created_at':
                    f.field = 'divergence_created_at'
                mapped.append(f)
        filter_sql, params = build_filter_sql(mapped)
        full_query = f"""
            SELECT
                nome_divergencia,
                sum(total_divergencia) as total_count
            FROM mview_divergence_{customer}
            WHERE 1=1
        """ + filter_sql + " GROUP BY nome_divergencia ORDER BY total_count DESC LIMIT 10"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [DivergenciaTipo(nomeDivergencia=r[0], totalCount=r[1]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_divergencia_analitico(self, customer: str = None, limit: int = 50, offset: int = 0, filters: Optional[List[FilterInput]] = None) -> List[DivergenciaAnalitica]:
        mapped = []
        if filters:
            for f in filters:
                if f.field == 'process_created_at':
                    f.field = 'validation_record_created_at'
                mapped.append(f)
        filter_sql, params = build_filter_sql(mapped)
        full_query = f"""
            SELECT id as id_divergencia,
                coalesce(validation_error_name, 'Sem Nome') as nome_divergencia,
                coalesce(associated_to_id, 0) as id_nota,
                coalesce(validation_target_value, 'Sem Valor') as validation_target_value,
                coalesce(validation_data_field_value, 'Sem Valor') as validation_data_field_value,
                validation_record_created_at
            FROM divergences
            WHERE c_id = '{customer}_prod'
        """ + filter_sql + f" ORDER BY validation_record_created_at DESC LIMIT {limit} OFFSET {offset}"

        def _query():
            print(full_query, params)
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [DivergenciaAnalitica(id=int(r[0]), nomeDivergencia=r[1], idNota=r[2],
                                             targetValue=r[3], fieldValue=r[4], createdAt=r[5]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_notas_aberto(self, grain: str = "month", customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[NotasAberto]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                date_trunc('{grain}', process_created_at)::text as {grain},
                sum(case when horas_em_aberto is not null then total_notas else 0 end) as total_em_aberto,
                sum(case when horas_em_aberto is not null and user_name is not null then total_notas else 0 end) as total_em_aberto_humanas
            FROM mview_process_{customer}
            WHERE horas_em_aberto is not null and user_name is not null
        """ + filter_sql + " GROUP BY 1 ORDER BY 1"

        def _query():
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [NotasAberto(date=r[0], totalEmAberto=int(r[1]), totalEmAbertoHumanas=r[2]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_notas_aberto_usuario(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[NotasAbertoUsuario]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                user_name,
                sum(total_notas) as total_count
            FROM mview_process_{customer}
            WHERE user_name is not null and horas_em_aberto is not null
        """ + filter_sql + " GROUP BY user_name ORDER BY total_count DESC LIMIT 10"

        def _query():
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [NotasAbertoUsuario(userName=r[0], totalCount=r[1]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_notas_aberto_tarefa(self, customer: str = None, filters: Optional[List[FilterInput]] = None) -> List[NotasAbertoTarefa]:
        filter_sql, params = build_filter_sql(filters)
        full_query = f"""
            SELECT
                last_task_name,
                sum(total_notas) as total_count
            FROM mview_process_{customer}
            WHERE user_name is not null and horas_em_aberto is not null
        """ + filter_sql + " GROUP BY last_task_name ORDER BY total_count DESC LIMIT 10"

        def _query():
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [NotasAbertoTarefa(nomeTarefa=r[0], totalCount=r[1]) for r in rows]

        return await asyncio.to_thread(_query)

    @strawberry.field
    async def get_notas_aberto_analitico(self, customer: str = None, limit: int = 50, offset: int = 0, filters: Optional[List[FilterInput]] = None) -> List[NotasAbertoAnalitica]:
        mapped = []
        if filters:
            for f in filters:
                if f.field == 'process_created_at':
                    f.field = 'created_at'
                mapped.append(f)
        filter_sql, params = build_filter_sql(mapped)
        full_query = f"""
            SELECT id, created_at, last_task_name, assigned_user
            FROM tax_documents
            WHERE c_id = '{customer}_prod'
            AND completed_at is null AND assigned_user is not null
        """ + filter_sql + f" ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}"

        def _query():
            with engine.connect() as conn:
                rows = conn.execute(text(full_query), params).fetchall()
                return [NotasAbertoAnalitica(id=int(r[0]), createdAt=r[1], nomeTarefa=r[2], userName=r[3]) for r in rows]

        return await asyncio.to_thread(_query)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
