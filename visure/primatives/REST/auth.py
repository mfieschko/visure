import requests

from visure import primatives

def authenticate(url, username, password, licensetype = "AUTHORING") -> dict:
    final_url = f'{url}/authenticate'
    payload = {
        "username": username,
        "password": password,
        "licenseType": licensetype
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", final_url, json=payload, headers=headers, params={"":""}, verify=primatives._do_verify).json()
    return response

def token_refresh(url, refreshToken):
    final_url = f'{url}/token/refresh'
    payload = {
        "refreshToken": refreshToken
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", final_url, json=payload, headers=headers, params={"":""}, verify=primatives._do_verify).json()
    return response

def logout(url: str, jwt_token: str) -> dict:
    final_url = f'{url}/logout'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(final_url, headers=headers, verify=primatives._do_verify)
    resp.raise_for_status()
    return resp
