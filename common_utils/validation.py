import os
import requests

def validate_payload(payload, model_type):
    validation_url = os.environ.get('VALIDATION_SERVICE_URL', 'http://localhost:5100/api/validate')
    try:
        resp = requests.post(validation_url, json={
            'model_type': model_type,
            'payload': payload
        }, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get('valid', False), data.get('errors', [])
    except Exception as e:
        return False, [str(e)] 