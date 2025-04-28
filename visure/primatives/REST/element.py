import requests
import aiohttp

def get_element_attributes(url, element_id : int, jwt_token: str):
    final_url = f'{url}/specification/element/{element_id}/attributes'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()

async def get_element_attributes_async(url, element_id : int, jwt_token: str):
    final_url = f'{url}/specification/element/{element_id}/attributes'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(final_url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


def create_element_in_specification(url, spec_id : int, jwt_token: str, parent_id = None, asChildren = False, numberOfElements = 1) -> dict:
    final_url = f'{url}/elements/add'
    if parent_id == None:
        parent_id = spec_id
    payload = {
        "specificationID": spec_id,
        "selectedElement": parent_id,
        "asChildren": asChildren,
        "numberOfElements": numberOfElements
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def get_description(url, element_id : int, jwt_token: str, parsed : bool = True):
    final_url = f'{url}/element/{element_id}/description'
    payload = {
        "parsed": parsed
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def set_description(url, element_id : int, jwt_token: str, text : str):
    final_url = f'{url}/element/{element_id}/description'
    payload = {
        "description": text
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    # return resp.json()

def set_code(url, element_id : int, jwt_token: str, text : str):
    final_url = f'{url}/element/code'
    payload = {
        "id": element_id,
        "code": text
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.put(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    # return resp.json()

def set_name(url, element_id : int, jwt_token: str, text : str):
    final_url = f'{url}/element/name'
    payload = {
        "id": element_id,
        "name": text
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.put(final_url, headers=headers, json=payload)
    resp.raise_for_status()
    # return resp.json()