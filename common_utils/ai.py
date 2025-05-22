import os
import requests

def call_ai_assistant(prompt, jwt_token=None):
    ai_url = os.environ.get('AI_ASSISTANT_SERVICE_URL', 'http://localhost:5200/api/ask')
    headers = {'Authorization': jwt_token} if jwt_token else {}
    try:
        resp = requests.post(ai_url, json={'prompt': prompt}, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get('response')
    except Exception as e:
        return f'AI service error: {str(e)}' 