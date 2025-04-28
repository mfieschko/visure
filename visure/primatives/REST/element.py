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

def get_available_relationships(url, source_id: int, target_id: int, jwt_token: str):
    """
    Get available relationship types between two elements.
    
    Args:
        url: Base URL for the Visure API
        source_id: ID of the source element
        target_id: ID of the target element
        jwt_token: Authentication token
        
    Returns:
        List of available relationship types with format:
        [{"sourceID": int, "targetID": int, "id": int, "name": str}]
    """
    final_url = f'{url}/elements/relationship/{source_id}/{target_id}'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def create_relationships(url, relationships: list, jwt_token: str):
    """
    Create relationships between elements.
    
    Args:
        url: Base URL for the Visure API
        relationships: List of relationship dictionaries with:
            - id: Relationship type ID
            - sourceID: Source element ID
            - targetID: Target element ID
            - isSuspect: Whether the link is suspect
            - projectID: Source project ID
            - targetProjectID: Target project ID
            - motiveName: Name of the relationship type
        jwt_token: Authentication token
        
    Returns:
        API response
    """
    final_url = f'{url}/elements/relationship/create'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(final_url, headers=headers, json=relationships)
    resp.raise_for_status()
    # return resp.json()

def modify_element_attribute(url, jwt_token: str, element_id: int, attribute_id:int, basetype: str, isMultivalued: bool, values: list):
    final_url = f'{url}/elements/relationship/create'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "parentId": element_id, # Item ID
        "id": attribute_id, # Attribute ID
        "baseType": basetype, # stored in visure\primatives\enums.py, or can be any string for custom type
        "isMultivalued": isMultivalued,
        "values": values
    }
    
    resp = requests.post(final_url, headers=headers, json=payload)
    resp.raise_for_status()