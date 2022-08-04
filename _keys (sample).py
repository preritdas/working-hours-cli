class Deta:
    """
    Where all your monthly log databases are stored.
    """
    project_key: str = ''


class Bitly:
    """
    Shorten long links in PDF reports.
    """
    access_token: str = ''
    

class RapidAPI:
    """
    Smart string capitalization, only if enabled config.ini.
    """
    api_key: str = ''
    