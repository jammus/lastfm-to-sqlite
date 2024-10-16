import pytest
from sqlite_utils import Database

from lastfm import fetch_artists_to_update, save_artist_details, save_artist_listen_date
from lastfm.db_setup import create_artist_table


@pytest.fixture
def db():
    database = Database(memory=True)
    create_artist_table(database)
    return database


@pytest.fixture
def db_with_artist_listens(db):
    artist_listens = [
        {
            "artist": "65daysofstatic",
            "uts_timestamp": 1234567890,
        },
        {
            "artist": "Tiny Moving Parts",
            "uts_timestamp": 3456789012,
        },
        {
            "artist": "Try Science",
            "uts_timestamp": 2345678901,
        },
    ]

    for listen in artist_listens:
        save_artist_listen_date(db, listen)
    return db


@pytest.mark.usefixtures("db_with_artist_listens")
def test_orders_by_recent_listens_descending(db):
    artists = list(fetch_artists_to_update(db))

    assert len(artists) == 3
    assert artists[0]["name"] == "Tiny Moving Parts"
    assert artists[1]["name"] == "Try Science"
    assert artists[2]["name"] == "65daysofstatic"


@pytest.mark.usefixtures("db_with_artist_listens")
def test_deprioritises_recently_updated_artists(db):
    save_artist_details(db, {"name": "Tiny Moving Parts"}, timestamp=4567890123)

    artists = list(fetch_artists_to_update(db))

    assert len(artists) == 3
    assert artists[0]["name"] == "Try Science"
    assert artists[1]["name"] == "65daysofstatic"
    assert artists[2]["name"] == "Tiny Moving Parts"


@pytest.mark.usefixtures("db_with_artist_listens")
def test_will_ignore_artists_updated_after_cutoff(db):
    save_artist_details(db, {"name": "Tiny Moving Parts"}, timestamp=4000000000)
    save_artist_details(db, {"name": "65daysofstatic"}, timestamp=3999999999)
    save_artist_details(db, {"name": "Try Science"}, timestamp=4000000001)

    artists = list(fetch_artists_to_update(db, cutoff=4000000000))

    assert len(artists) == 1
    assert artists[0]["name"] == "65daysofstatic"


@pytest.mark.usefixtures("db_with_artist_listens")
def test_accepts_a_limit(db):
    artists = list(fetch_artists_to_update(db, limit=2))

    assert len(artists) == 2
    assert artists[0]["name"] == "Tiny Moving Parts"
    assert artists[1]["name"] == "Try Science"
