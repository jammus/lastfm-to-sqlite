import os
import json
import pytest
import datetime
from lastfm import LastFM, process_loved_tracks_response, process_recent_tracks_response

def load_json(filename):
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def page():    
    page = load_json("sample_recent_tracks_dump.json")
    return page['recenttracks']['track']

@pytest.fixture
def loves_page():    
    page = load_json("sample_loves_dump.json")
    return page['lovedtracks']['track']

@pytest.fixture
def date():
    return datetime.datetime.today().strftime(LastFM.DATE_FORMAT)

@pytest.fixture
def apikey():
    return "342ec3b62b2501514199059eed07c75a"

@pytest.fixture
def api(apikey, date):
    return LastFM(api=apikey, username="way4Music", start_date=date)

def test_convert_to_timestamp(api, date):
    assert isinstance(api._convert_to_timestamp(date), int)

def test_process_recent_tracks_response(page):
    data = process_recent_tracks_response(page)
    song = next(data)
    assert isinstance(song, dict)
    assert set(song.keys()) == {"artist", "album", "song", "uts_timestamp", "datetime"}
    assert song["artist"] == "Lera Lynn"
    assert song["song"] == "Lately (From The HBO Series \"True Detective\")"
    assert song["album"] == "True Detective (Music From the HBO Series)"
    assert song["uts_timestamp"] == 1603622207
    assert song["datetime"] == "25 Oct 2020, 10:36"

def test_process_loved_tracks_response(loves_page):
    data = process_loved_tracks_response(loves_page)
    love = next(data)
    assert isinstance(love, dict)
    assert set(love.keys()) == {"artist", "song", "uts_timestamp", "datetime"}
    assert love["artist"] == "65daysofstatic"
    assert love["song"] == "SynthFlood"
    assert love["uts_timestamp"] == 1725597832
    assert love["datetime"] == "06 Sep 2024, 04:43"
