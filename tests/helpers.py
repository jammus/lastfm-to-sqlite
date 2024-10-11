import os
import requests

from lastfm import ApiClient


def load_file(filename):
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def api_client() -> ApiClient:
    return {
        "base_url": "http://ws.audioscrobbler.com/2.0",
        "api_key": "abcdefg",
        "username": "jammus",
        "session": requests.Session(),
    }
