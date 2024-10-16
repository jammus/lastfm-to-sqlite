import httpretty
from httpretty import httprettified

from lastfm import fetch_album
from tests.helpers import api_client, load_file


@httprettified
def test_requests_details_from_album_info_method():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_album(api_client(), "Do Not Lay Waste To Homes...", artist="El Huervo")

    assert httpretty.last_request().querystring["method"][0] == "album.getinfo"


@httprettified
def test_requests_details_for_supplied_album_artist_pair():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_album(api_client(), "Do Not Lay Waste To Homes...", artist="El Huervo")

    querystring = httpretty.last_request().querystring
    assert querystring["album"][0] == "Do Not Lay Waste To Homes..."
    assert querystring["artist"][0] == "El Huervo"


@httprettified
def test_does_not_autocorrect():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")

    fetch_album(api_client(), "Do Not Lay Waste To Homes...", artist="El Huervo")

    assert httpretty.last_request().querystring["autocorrect"][0] == "0"


@httprettified
def test_returns_album_details():
    response = load_file("sample_album_response.json")
    httpretty.register_uri(
        httpretty.GET, "http://ws.audioscrobbler.com/2.0", body=response
    )

    album = fetch_album(
        api_client(), "Do Not Lay Waste To Homes...", artist="El Huervo"
    )

    assert album["name"] == "Fetch"
    assert album["artist"] == "Melt-Banana"
    assert album["url"] == "https://www.last.fm/music/Melt-Banana/Fetch"
    assert album["image_id"] == "ca2f75a0958349d2803f5afd9aba6936"
