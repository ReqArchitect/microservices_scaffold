import requests

def post_with_jwt(url, json, jwt_token, timeout=5):
    headers = {'Authorization': jwt_token} if jwt_token else {}
    resp = requests.post(url, json=json, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json() 