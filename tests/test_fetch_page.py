import pytest
import httpretty
from httpretty import httprettified
import requests

from lastfm import fetch_page


@httprettified
def test_makes_request_to_lastfm_api():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    fetch_page(session, None)

    last_request = httpretty.last_request()
    assert last_request.host == "ws.audioscrobbler.com"
    assert last_request.path.startswith("/2.0")


@httprettified
def test_sends_method_parameter():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    fetch_page(session, "user.getrecenttracks")

    assert httpretty.last_request().querystring["method"][0] == "user.getrecenttracks"


@httprettified
def test_requested_format_is_always_json():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    fetch_page(session, "user.getrecenttracks")

    assert httpretty.last_request().querystring["format"][0] == "json"


@httprettified
def test_sends_all_provided_params():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    fetch_page(session, "user.getrecenttracks", { "page": 20, "user": "jammus" })

    assert httpretty.last_request().querystring["page"][0] == "20"
    assert httpretty.last_request().querystring["user"][0] == "jammus"


@httprettified
def test_returns_parsed_json_response():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body="{\"success\": true}")
    session = requests.session()

    response = fetch_page(session, "user.getrecenttracks", { "page": 20, "user": "jammus" })

    assert response["success"] is True


@httprettified
def test_raises_on_failure():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           status=500)
    session = requests.session()

    with pytest.raises(Exception):
        fetch_page(session, "user.getrecenttracks", { "page": 20, "user": "jammus" })

    assert len(httpretty.latest_requests()) == 5


@httprettified
def test_retries_failed_requests_5_times():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           status=500)
    session = requests.session()

    with pytest.raises(Exception):
        fetch_page(session, "user.getrecenttracks", { "page": 20, "user": "jammus" })

    assert len(httpretty.latest_requests()) == 5
