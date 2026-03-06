import requests

API_URL = "http://localhost:8000/graphql"

def fetch_graphql_data(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"GraphQL Error: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Connection Error: {e}")
        return None
    
# def get_filter_options(customer):
#     query = """
#     query GetOptions($customer: String!) {
#         fluxos: get_distinct_fluxos(customer: $customer)
#         fornecedores: get_distinct_suppliers(customer: $customer)
#         tomadores: get_distinct_customers(customer: $customer)
#         moedas: get_distinct_currencies(customer: $customer)
#     }
#     """
#     payload = {'query': query, 'variables': {'customer': customer}}
#     res = fetch_graphql_data(payload)
#     return res['data'] if res else {}

def get_full_dashboard_data(grain="month", customer=None, filters=None):
    """
    Traz Stories 1, 2 e 3 em uma única chamada de rede (Batching).
    Substitui a necessidade de chamar get_captura, get_captura_fornecedores e get_captura_cidades separadamente.
    """
    query = """
    query GetDashboard($filters: [FilterInput!], $customer: String!, $grain: String!) {
        series: getCaptura(filters: $filters, customer: $customer, grain: $grain) {
            date totalCount totalAuto documentType
        }
        suppliers: getCapturaFornecedores(filters: $filters, customer: $customer) {
            supplierCnpj totalCount totalAuto documentType
        }
        cities: getCapturaCidades(filters: $filters, customer: $customer) {
            currency totalCount totalAuto documentType
        }
    }
    """
    payload = {
        'query': query, 
        'variables': {
            'filters': filters if filters is not None else [],
            'customer': customer,
            'grain': grain
        }
    }
    
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        # Retorna o dicionário completo com 'series', 'suppliers' e 'cities'
        return res['data']
    return {"series": [], "suppliers": [], "cities": []}

def get_analitico(limit=10, offset=0, customer=None, filters=None):
    """
    Mantida separada para Story 4 devido à paginação e grande volume de dados.
    """
    query = """
    query GetCapturaAnalitico($limit: Int!, $offset: Int!, $customer: String!, $filters: [FilterInput!]) {
        getCapturaAnalitico(limit: $limit, offset: $offset, customer: $customer, filters: $filters) {
            id
            supplierCnpj
            issueDate
            provider
            totalValue
            documentType
        }
    }
    """
    payload = {
        'query': query,
        'variables': {
            'limit': limit,
            'offset': offset,
            'customer': customer,
            'filters': filters or []
        }
    }
    
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        return res['data'].get('getCapturaAnalitico', [])
    return []