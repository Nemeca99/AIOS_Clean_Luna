import requests

def fetch_user_data(user_id):
    # Fetch user from API
    response = requests.get(f"https://api.example.com/users/{user_id}", timeout=10.0)
    return response.json()

def update_user(user_id, data):
    response = requests.post(f"https://api.example.com/users/{user_id}", json=data, timeout=10.0)
    return response.status_code
