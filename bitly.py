import requests
import keys


def bitly(long_link: str) -> str:
    """Shortens link using the bitly API."""
    if not isinstance(long_link, str):
        raise Exception("You must provide a string.")

    headers = {
        'Authorization': f'Bearer {keys.Bitly.access_token}',
        'Content-Type': 'application/json'
    }

    data = ' {"long_url": "' + long_link + '" } '
    
    response = requests.post(url="https://api-ssl.bitly.com/v4/shorten", headers=headers, data=data)
    return response.json()['link']
