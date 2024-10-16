import httpretty
from httpretty import httprettified

from lastfm import fetch_artist
from tests.helpers import api_client, load_file


@httprettified
def test_requests_details_from_artist_method():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_artist(api_client(), "El Huervo")

    assert httpretty.last_request().querystring["method"][0] == "artist.getinfo"


@httprettified
def test_requests_details_for_supplied_artist_name():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_artist(api_client(), "El Huervo")

    assert httpretty.last_request().querystring["artist"][0] == "El Huervo"

    fetch_artist(api_client(), "Melt-Banana")

    assert httpretty.last_request().querystring["artist"][0] == "Melt-Banana"


@httprettified
def test_does_not_autocorrect():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_artist(api_client(), "El Huervo")

    assert httpretty.last_request().querystring["autocorrect"][0] == "0"


@httprettified
def test_send_supplied_params():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_artist(api_client(), "El Huervo", params={"api_key": "abcdefg", "user":
                                               "jammus"})

    assert httpretty.last_request().querystring["api_key"][0] == "abcdefg"
    assert httpretty.last_request().querystring["user"][0] == "jammus"


@httprettified
def test_returns_basic_artist_details():
    response_body = load_file("sample_artist_response.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                            body=response_body)

    artist = fetch_artist(api_client(), "Melt-Banana")

    assert artist["name"] == "Melt-Banana"
    assert artist["url"] == "https://www.last.fm/music/Melt-Banana"


@httprettified
def test_extracts_image_id():
    response_body = load_file("sample_artist_response.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                            body=response_body)

    artist = fetch_artist(api_client(), "Melt-Banana")

    assert artist["image_id"] == "d93fb932f7a34434bed332cbeb1b3ae6"
