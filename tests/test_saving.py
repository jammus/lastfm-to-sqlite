import pytest
from sqlite_utils import Database

from lastfm import save_recent_track, save_track


@pytest.fixture
def db():
    return Database(memory=True)


def test_saving_a_single_recent_track_creates_record_in_playlist_table(db: Database):
    recent_track = {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }

    save_recent_track(db, recent_track)

    tracks = list(db.query("select * from playlist"))
    assert len(tracks) == 1
    assert tracks[0] == {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }


def test_save_two_recent_tracks_creates_two_records_in_playlist_table(db: Database):
    recent_track = [{
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }, {
        "artist": "Colossal Squid",
        "album": "A Haunted Tongue",
        "song": "Fewston",
        "uts_timestamp": 1725967902,
        "datetime": "10 Sep 2024, 11:31"
    }]

    save_recent_track(db, recent_track[0])
    save_recent_track(db, recent_track[1])

    tracks = list(db.query("select * from playlist"))
    assert len(tracks) == 2
    assert tracks[0]["song"] == "SynthFlood"
    assert tracks[1]["song"] == "Fewston"


def test_saving_the_same_recent_track_twice_only_creates_one_record(db: Database):
    recent_track = {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }

    save_recent_track(db, recent_track)
    save_recent_track(db, recent_track)

    tracks = list(db.query("select * from playlist"))
    assert len(tracks) == 1


def test_saving_recent_track_to_track_table_creates_simple_record(db: Database):
    recent_track = {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }

    save_track(db, recent_track)

    tracks = list(db.query("select * from tracks"))
    assert len(tracks) == 1
    assert tracks[0] == {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
    }


def test_saving_the_same_track_twice_only_creates_one_record(db: Database):
    recent_track = {
        "artist": "65daysofstatic",
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1725597832,
        "datetime": "06 Sep 2024, 04:43",
    }

    save_track(db, recent_track)
    save_track(db, recent_track)

    tracks = list(db.query("select * from tracks"))
    assert len(tracks) == 1
