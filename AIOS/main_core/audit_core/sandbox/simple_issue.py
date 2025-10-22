import requests

def fetch_data(url):
    response = requests.get(url, timeout=10.0)
    response.raise_for_status()
    return response.json()

def post_data(url, data):
    response = requests.post(url, json=data, timeout=10.0)
    response.raise_for_status()
    return response.json()
