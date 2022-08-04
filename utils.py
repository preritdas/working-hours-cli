"""
Utils to be used by other modules, including title capitalization, etc.
"""
# Non-local imports
import requests

# Project modules
import _keys 
from config import Config


# ---- Language ----

def capitalize_title(title: str) -> str:
    if not isinstance(title, str):
        raise Exception("You can only capitalize string titles.")

    # If smart capitalization is disabled
    if not Config.smart_cap_preference:
        return title.title()

    # Separate words with %20
    title = title.replace(' ', '%20')

    # Make the request
    url = f"https://capitalize-my-title.p.rapidapi.com/title/{title}"
    headers = {
        "X-RapidAPI-Key": _keys.RapidAPI.api_key,
        "X-RapidAPI-Host": "capitalize-my-title.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)

    return response.json()['data']['output']
