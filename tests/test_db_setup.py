import pytest
from sqlite_utils import Database
from lastfm import save_recent_track
from lastfm.db_setup import (create_album_detail_view,
                             create_album_view,
                             create_artist_view,
                             create_artist_detail_view,
                             create_track_detail_view,
                             create_track_view)


@pytest.fixture
def db():
    return Database(memory=True)


@pytest.fixture
def recent_tracks():
    return [{
        "artist": "65daysofstatic",    # Last 65dos listen
        "song": "SynthFlood",
        "album": "Utopian Frequencies",
        "uts_timestamp": 1726597832,
    }, {
        "artist": "65daysofstatic",    # First 65dos listen
        "song": "The Fall of Math",
        "album": "The Fall of Math",   # First Fall of Math listen
        "uts_timestamp": 1724599832,
    }, {
        "artist": "65daysofstatic",
        "song": "Retreat! Retreat!",
        "album": "The Fall of Math",
        "uts_timestamp": 1725599822,
    }, {
        "artist": "65daysofstatic",
        "song": "Retreat! Retreat!",   # Last Retreat listen
        "album": "The Fall of Math",   # Last Fall of Math listen
        "uts_timestamp": 1725599832,
    }, {
        "artist": "65daysofstatic",
        "song": "Retreat! Retreat!",   # First Retreat listen
        "album": "The Fall of Math",
        "uts_timestamp": 1725499832,
    }, {
        "artist": "Do Make Say Think", # First DMST listen
        "song": "War On Want",
        "album": "Winter Hymn Country Hymn Secret Hymn",
        "uts_timestamp": 1625499833,
    }]


def test_artist_detail_view_records_first_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    create_artist_view(db)
    create_artist_detail_view(db)

    [artist] = list(db.query(
        "select * from v_artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["discovered"] == 1724599832


def test_artist_detail_view_records_most_recent_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    create_artist_view(db)
    create_artist_detail_view(db)

    [artist] = list(db.query(
        "select * from v_artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["last_listened"] == 1726597832


def test_track_detail_view_records_first_and_last_listen(db: Database,
                                                         recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    create_track_view(db)
    create_track_detail_view(db)

    [track] = list(db.query(
        "select * from v_track_details where name = :track and artist = :artist",
        { "artist": "65daysofstatic", "track": "Retreat! Retreat!" }
    ))

    assert track["discovered"] == 1725499832
    assert track["last_listened"] == 1725599832


def test_album_detail_view_records_first_and_last_listen(db: Database,
                                                         recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    create_album_view(db)
    create_album_detail_view(db)

    [album] = list(db.query(
        "select * from v_album_details where name = :album and artist = :artist",
        { "artist": "65daysofstatic", "album": "The Fall of Math" }
    ))

    assert album["discovered"] == 1724599832
    assert album["last_listened"] == 1725599832
