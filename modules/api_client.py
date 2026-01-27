import requests

API_URL = "http://localhost:8000/graphql"

def fetch_graphql_data(query_string):
    try:
        response = requests.post(API_URL, json={'query': query_string})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def get_captura():
    query = """
    query {
        getCaptura {
            date
            totalCount
            totalAuto
            documentType
        }
    }
    """
    result = fetch_graphql_data(query)
    if result and 'data' in result:
        return result['data'].get('getCaptura', [])
    return []