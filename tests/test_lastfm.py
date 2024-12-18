import os
import json
import pytest
import datetime
from lastfm import DATE_FORMAT, LastFM, convert_to_timestamp, process_tracks_response


def load_json(filename):
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def recenttracks_page():
    page = load_json("sample_recent_tracks_dump.json")
    return page["recenttracks"]["track"]


@pytest.fixture
def recenttracks_with_now_playing_page():
    page = load_json("sample_recent_tracks_dump_with_nowplaying.json")
    return page["recenttracks"]["track"]


@pytest.fixture
def recenttracks_with_no_image():
    page = load_json("sample_recent_tracks_no_image_dump.json")
    return page["recenttracks"]["track"]


@pytest.fixture
def loves_page():
    page = load_json("sample_loves_dump.json")
    return page["lovedtracks"]["track"]


@pytest.fixture
def date():
    return datetime.datetime.today().strftime(DATE_FORMAT)


@pytest.fixture
def apikey():
    return "342ec3b62b2501514199059eed07c75a"


def test_convert_to_timestamp(date):
    assert isinstance(convert_to_timestamp(date), int)


def test_covert_to_timestamp_returns_none_when_date_is_missing():
    assert convert_to_timestamp(None) is None


def test_process_recent_tracks_response(recenttracks_page):
    data = process_tracks_response(recenttracks_page)
    song = next(data)
    assert isinstance(song, dict)
    assert song["artist"] == "Lera Lynn"
    assert song["song"] == 'Lately (From The HBO Series "True Detective")'
    assert song["album"] == "True Detective (Music From the HBO Series)"
    assert song["uts_timestamp"] == 1603622207
    assert song["datetime"] == "25 Oct 2020, 10:36"


def test_process_loved_tracks_response(loves_page):
    data = process_tracks_response(loves_page)
    love = next(data)
    assert isinstance(love, dict)
    assert love["artist"] == "65daysofstatic"
    assert love["song"] == "SynthFlood"
    assert love["uts_timestamp"] == 1725597832
    assert love["datetime"] == "06 Sep 2024, 04:43"


def test_skips_now_playing_tracks(recenttracks_with_now_playing_page):
    data = process_tracks_response(recenttracks_with_now_playing_page)
    track = next(data)
    assert isinstance(track, dict)
    assert track["artist"] == "Colossal Squid"


def test_track_image_id_is_blank_by_default(recenttracks_with_no_image):
    data = process_tracks_response(recenttracks_with_no_image)
    track = next(data)
    assert track.get("image_id", None) is None


def test_track_image_id_hash_with_all_other_details_stripped(recenttracks_page):
    data = process_tracks_response(recenttracks_page)
    track = next(data)
    assert track.get("image_id", None) == "fb0529f082462f505cd0902734c174c8"
