import requests

def get_projects(url, jwt_token: str) -> dict:
    final_url = f'{url}/projects'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def get_project_info(url, project_id : int, jwt_token: str) -> dict:
    final_url = f'{url}/project/{project_id}'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def set_active_project(url, project_id : int, group : int, jwt_token: str):
    final_url = f'{url}/project/current'
    payload = {
        "project": project_id,
        "group": group,
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def get_attribute_types_in_project(url, jwt_token: str):
    final_url = f'{url}/project/attribute/types'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()