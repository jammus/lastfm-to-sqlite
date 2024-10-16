import pytest
from sqlite_utils import Database

from lastfm import save_recent_track
from lastfm.db_setup import create_album_table, create_artist_table, create_track_table


@pytest.fixture
def db():
    database = Database(memory=True)
    create_artist_table(database)
    create_track_table(database)
    create_album_table(database)
    return database


@pytest.fixture
def recent_tracks():
    return [
        {
            "artist": "65daysofstatic",  # Last 65dos listen
            "song": "SynthFlood",
            "album": "Utopian Frequencies",
            "uts_timestamp": 1726597832,
            "image_id": "abcdefg",
        },
        {
            "artist": "65daysofstatic",  # First 65dos listen
            "song": "The Fall of Math",
            "album": "The Fall of Math",  # First Fall of Math listen
            "uts_timestamp": 1724599832,
        },
        {
            "artist": "65daysofstatic",
            "song": "Retreat! Retreat!",
            "album": "The Fall of Math",
            "uts_timestamp": 1725599822,
        },
        {
            "artist": "65daysofstatic",
            "song": "Retreat! Retreat!",  # Last Retreat listen
            "album": "The Fall of Math",  # Last Fall of Math listen
            "uts_timestamp": 1725599832,
        },
        {
            "artist": "65daysofstatic",
            "song": "Retreat! Retreat!",  # First Retreat listen
            "album": "The Fall of Math",
            "uts_timestamp": 1725499832,
        },
        {
            "artist": "Do Make Say Think",  # First DMST listen
            "song": "War On Want",
            "album": "Winter Hymn Country Hymn Secret Hymn",
            "uts_timestamp": 1625499833,
        },
        {
            "artist": "Told Slant",  # First DMST listen
            "song": "Parking Lots",
            "album": "",
            "uts_timestamp": 1625499833,
        },
    ]


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
    recent_track = [
        {
            "artist": "65daysofstatic",
            "song": "SynthFlood",
            "album": "Utopian Frequencies",
            "uts_timestamp": 1725597832,
            "datetime": "06 Sep 2024, 04:43",
        },
        {
            "artist": "Colossal Squid",
            "album": "A Haunted Tongue",
            "song": "Fewston",
            "uts_timestamp": 1725967902,
            "datetime": "10 Sep 2024, 11:31",
        },
    ]

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


def test_artist_table_records_first_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    [artist] = list(
        db.query(
            "select * from artist_details where name = :artist",
            {"artist": "65daysofstatic"},
        )
    )

    assert artist["discovered"] == 1724599832


def test_artist_table_records_most_recent_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    [artist] = list(
        db.query(
            "select * from artist_details where name = :artist",
            {"artist": "65daysofstatic"},
        )
    )

    assert artist["last_listened"] == 1726597832


def test_track_table_records_first_and_last_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    [track] = list(
        db.query(
            "select * from track_details where name = :track and artist = :artist",
            {"artist": "65daysofstatic", "track": "Retreat! Retreat!"},
        )
    )

    assert track["discovered"] == 1725499832
    assert track["last_listened"] == 1725599832


def test_saving_track_records_image_id(db: Database, recent_tracks):
    recent_track = recent_tracks[0]
    save_recent_track(db, recent_track)
    [track] = list(
        db.query(
            "select * from track_details where name = :track and artist = :artist",
            {"artist": recent_track["artist"], "track": recent_track["song"]},
        )
    )
    assert track.get("image_id", "") == "abcdefg"


def test_album_table_records_first_and_last_listen(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    [album] = list(
        db.query(
            "select * from album_details where name = :album and artist = :artist",
            {"artist": "65daysofstatic", "album": "The Fall of Math"},
        )
    )

    assert album["discovered"] == 1724599832
    assert album["last_listened"] == 1725599832


def test_does_not_save_albums_when_no_album_name_is_given(db: Database, recent_tracks):
    for recent_track in recent_tracks:
        save_recent_track(db, recent_track)

    albums = list(
        db.query(
            "select * from album_details where artist = :artist",
            {"artist": "Told Slant"},
        )
    )

    assert len(albums) == 0
