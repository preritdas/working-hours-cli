"""
Utils to be used by other modules, including title capitalization, etc.
"""
# Non-local imports
import requests

# Local imports
import enum

# Project modules
import keys 
from config import Config


# ---- Language ----


class CapitalizationMethod(enum.Enum):
    SMART = enum.auto()
    DEFAULT = enum.auto()


def capitalize_title(title: str, method_force: str = None) -> str:
    if not isinstance(title, str):
        raise Exception("You can only capitalize string titles.")

    # Determine method

    if not method_force:
        method = Config.smart_cap_preference
    else:
        if method_force.lower() == "smart" or Config.smart_cap_preference:
            method = CapitalizationMethod.SMART
        else:
            method = CapitalizationMethod.DEFAULT

    # If smart capitalization is disabled
    if method == CapitalizationMethod.DEFAULT:
        return title.title()

    # Separate words with %20
    title = title.replace(' ', '%20')

    # Make the request
    url = f"https://capitalize-my-title.p.rapidapi.com/title/{title}"
    headers = {
        "X-RapidAPI-Key": keys.RapidAPI.api_key,
        "X-RapidAPI-Host": "capitalize-my-title.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)

    return response.json()['data']['output']
