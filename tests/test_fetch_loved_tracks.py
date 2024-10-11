import httpretty
from httpretty import httprettified
import requests

from lastfm import ApiClient, fetch_loved_tracks
from tests.helpers import load_file


def api_client() -> ApiClient:
    return {
        "base_url": "http://ws.audioscrobbler.com/2.0",
        "api_key": "abcdefg",
        "username": "jammus",
        "session": requests.Session(),
    }


@httprettified
def test_requests_details_from_user_loved_tracks():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body="{}")

    next(fetch_loved_tracks(api_client()))

    assert httpretty.last_request().querystring["method"][0] == "user.getlovedtracks"


@httprettified
def test_returns_loves_in_standard_track_format():
    response_body = load_file("sample_loves_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)

    love, _ = next(fetch_loved_tracks(api_client()))

    assert love["song"] == "SynthFlood"
    assert love["artist"] == "65daysofstatic"
    assert love["uts_timestamp"] == 1725597832


@httprettified
def test_returns_loves_metadata():
    response_body = load_file("sample_loves_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)

    _, metadata = next(fetch_loved_tracks(api_client()))

    assert metadata["total"] == "793"
