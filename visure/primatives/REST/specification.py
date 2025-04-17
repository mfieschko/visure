import requests


def get_specifications(url, jwt_token: str) -> dict:
    final_url = f'{url}/specification/hierarchy/tolist'
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(final_url, headers=headers)
    resp.raise_for_status()
    return resp.json()