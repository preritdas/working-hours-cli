"""
Read and parse keys.
"""
import configparser
import os


current_dir = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(keys_path := os.path.join(current_dir, "keys.ini")):
    raise FileNotFoundError("You must have a keys.ini file.")

keys = configparser.RawConfigParser()
keys.read(keys_path)


class Deta:
    project_key: str = keys["Deta"]["project_key"]


class Bitly:
    access_token: str = keys["Bitly"]["access_token"]


class RapidAPI:
    api_key: str = keys["RapidAPI"]["api_key"]
