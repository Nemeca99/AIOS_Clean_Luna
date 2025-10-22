#!/usr/bin/env python3
import requests

try:
    r = requests.get('http://localhost:1234/v1/models', timeout=2)
    print(f'LM Studio Status: {r.status_code}')
    data = r.json()
    models = data.get('data', [])
    print(f'Models loaded: {len(models)}')
    for model in models:
        print(f'  - {model.get("id", "unknown")}')
except requests.exceptions.ConnectionError:
    print('LM Studio: NOT RUNNING')
    print('Please start LM Studio and load a model')
except Exception as e:
    print(f'LM Studio: Error - {e}')

