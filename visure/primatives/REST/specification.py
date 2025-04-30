import requests

from visure import primatives

def get_specifications(url, jwt_token: str) -> dict:
    final_url = f'{url}/specification/hierarchy/tolist'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    payload = ""
    resp = requests.get(final_url, headers=headers, data=payload, verify=primatives._do_verify)
    resp.raise_for_status()
    return resp.json()

def get_elements_in_specification(url, spec_id : int, jwt_token: str, ignoreActiveFilters = True, text_to_search = None) -> dict:
    final_url = f'{url}/specification/{spec_id}/items'
    payload = {
        "id": spec_id,
        "ignoreActiveFilters": ignoreActiveFilters,
        "text_to_search" : text_to_search
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers, json=payload, verify=primatives._do_verify)
    resp.raise_for_status()
    return resp.json()

def get_attributes_in_specification(url, spec_id : int, jwt_token: str, includeAttrsRequirements = True):
    final_url = f'{url}/specification/{spec_id}/attributes'
    payload = {
        "specId": spec_id,
        "includeAttrsRequirements": includeAttrsRequirements
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers, json=payload, verify=primatives._do_verify)
    resp.raise_for_status()
    return resp.json()