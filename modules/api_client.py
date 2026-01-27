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

def get_captura(filters=None):
    query = """
    query GetCaptura($filters: [FilterInput!]) {
        getCaptura(filters: $filters) {
            date
            totalCount
            totalAuto
        }
    }
    """
    # Ensure filters is an empty list if None, to satisfy [FilterInput!]
    payload = {
        'query': query, 
        'variables': {'filters': filters if filters is not None else []}
    }
    res = fetch_graphql_data(payload)
    if res and 'data' in res:
        return res['data'].get('getCaptura', [])
    return []