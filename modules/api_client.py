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

def get_captura(grain="month", filters=None):
    query = """
    query GetCaptura($filters: [FilterInput!], $grain: String!) {
        getCaptura(filters: $filters, grain: $grain) {
            date
            totalCount
            totalAuto
            documentType
            supplierName
            invoiceCityName
        }
    }
    """
    payload = {
        'query': query, 
        'variables': {
            'filters': filters if filters is not None else [],
            'grain': grain
        }
    }
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        return res['data'].get('getCaptura', [])
    return []