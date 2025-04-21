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
