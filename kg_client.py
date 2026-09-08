import requests

KG_URL = "http://127.0.0.1:5001/graph/update"

def push_to_knowledge_graph(data: dict):
    r = requests.post(KG_URL, json=data, timeout=30)
    r.raise_for_status()
    return r.json()
