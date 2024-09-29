import os
import httpretty
from httpretty import httprettified
import requests

from lastfm import fetch_pages


def load_file(filename):
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@httprettified
def test_fetches_from_lastfm_api():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    next(fetch_pages(session, "user.getrecenttracks", "recenttracks", "track"))

    last_request = httpretty.last_request()
    assert last_request.querystring["method"][0] == "user.getrecenttracks"
    assert last_request.host == "ws.audioscrobbler.com"
    assert last_request.path.startswith("/2.0")


@httprettified
def test_fetches_first_page_of_200_items_by_default():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    next(fetch_pages(session, "user.getrecenttracks", "recenttracks", "track"))

    assert httpretty.last_request().querystring["page"][0] == "1"
    assert httpretty.last_request().querystring["limit"][0] == "200"


@httprettified
def test_sends_through_all_other_parameters():
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0")
    session = requests.session()

    next(fetch_pages(session, "user.getrecenttracks", "recenttracks", "track",
                {"user": "jammus", "extended": "1"}))

    assert httpretty.last_request().querystring["user"][0] == "jammus"
    assert httpretty.last_request().querystring["extended"][0] == "1"


@httprettified
def test_returns_parsed_json_under_specified_root_item_name():
    response_body = load_file("sample_recent_tracks_single_page_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)
    session = requests.session()

    response, _ = next(fetch_pages(session, "user.getrecenttracks",
                                   "recenttracks", "track"))

    assert len(response) == 200
    assert response[0].get("name") == "Lately (From The HBO Series \"True Detective\")"


@httprettified
def test_returns_attr_block_as_additional_metadata():
    response_body = load_file("sample_recent_tracks_single_page_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)
    session = requests.session()

    _, metadata = next(fetch_pages(session, "user.getrecenttracks",
                                   "recenttracks", "track"))

    assert metadata == {
        "page": "1",
        "total": "200",
        "user": "Way4Music",
        "perPage": "200",
        "totalPages": "1"
    }


@httprettified
def test_fetches_all_pages():
    response_body = load_file("sample_recent_tracks_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)
    session = requests.session()

    data = list(fetch_pages(session, "user.getrecenttracks", "recenttracks",
                            "track"))

    assert len(httpretty.latest_requests()) == 7


@httprettified
def test_works_with_loved_tracks():
    response_body = load_file("sample_loves_dump.json")
    httpretty.register_uri(httpretty.GET, "http://ws.audioscrobbler.com/2.0",
                           body=response_body)
    session = requests.session()

    data = list(fetch_pages(session, "user.getlovedtracks", "lovedtracks",
                            "track"))

    last_request = httpretty.last_request()
    assert last_request.querystring["method"][0] == "user.getlovedtracks"
    assert len(httpretty.latest_requests()) == 16

    loves, metadata = data[0]
    assert loves[0].get("name") == "SynthFlood"
    assert metadata["total"] == "793"
