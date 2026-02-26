import requests

API_URL = "http://localhost:8000/graphql"

def fetch_graphql_data(payload): # Rename argument for clarity
    try:
        # Note: we send the payload directly as json
        response = requests.post(API_URL, json=payload)
        if response.status_code != 200:
            print(f"GraphQL Error: {response.text}") # This will help you debug
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Connection Error: {e}")
        return None

def get_captura(grain="month", customer=None, filters=None):
    query = """
    query GetCaptura($filters: [FilterInput!], $customer: String!, $grain: String!) {
        getCaptura(filters: $filters, customer: $customer, grain: $grain) {
            date
            totalCount
            totalAuto
            documentType
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
        return res['data'].get('getCaptura', [])
    return []

def get_captura_fornecedores(customer=None, filters=None):
    query = """
    query GetCapturaFornecedores($filters: [FilterInput!], $customer: String!) {
        getCapturaFornecedores(filters: $filters, customer: $customer) {
            supplierCnpj
            totalCount
            totalAuto
            documentType
        }
    }
    """
    payload = {
        'query': query, 
        'variables': {
            'filters': filters if filters is not None else [],
            'customer': customer
        }
    }
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        return res['data'].get('getCapturaFornecedores', [])
    return []

def get_captura_cidades(customer=None, filters=None):
    query = """
    query GetCapturaCidades($filters: [FilterInput!], $customer: String!) {
        getCapturaCidades(filters: $filters, customer: $customer) {
            currency
            totalCount
            totalAuto
            documentType
        }
    }
    """
    payload = {
        'query': query, 
        'variables': {
            'filters': filters if filters is not None else [],
            'customer': customer
        }
    }
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        return res['data'].get('getCapturaCidades', [])
    return []

def get_analitico(limit=10, offset=0, customer=None, filters=None):
    # A query agora pede limit e offset para o servidor
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