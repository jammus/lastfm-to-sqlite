import pytest
from sqlite_utils import Database

from lastfm import fetch_albums_to_update, save_album_details, save_album_listen_date
from lastfm.db_setup import create_album_table


@pytest.fixture
def db():
    database = Database(memory=True)
    create_album_table(database)
    return database


@pytest.fixture
def db_with_album_listens(db):
    album_listens = [
        {
            "album": "The Fall of Math",
            "artist": "65daysofstatic",
            "uts_timestamp": 1234567890,
        },
        {
            "album": "Tiny Moving Parts",
            "artist": "Tiny Moving Parts",
            "uts_timestamp": 3456789012,
        },
        {
            "album": "Next",
            "artist": "Trying Science",
            "uts_timestamp": 2345678901,
        },
    ]

    for listen in album_listens:
        save_album_listen_date(db, listen)
    return db


@pytest.mark.usefixtures("db_with_album_listens")
def test_orders_by_recent_listen_deprioritising_recently_updated_albums(db):
    save_album_details(
        db,
        {
            "name": "Tiny Moving Parts",
            "artist": "Tiny Moving Parts",
        },
        timestamp=4567890123,
    )

    albums = list(fetch_albums_to_update(db))

    assert len(albums) == 3
    assert albums[0]["name"] == "Next"
    assert albums[1]["name"] == "The Fall of Math"
    assert albums[2]["name"] == "Tiny Moving Parts"


@pytest.mark.usefixtures("db_with_album_listens")
def test_will_ignore_albums_updated_after_cutoff(db):
    save_album_details(
        db,
        {
            "name": "Tiny Moving Parts",
            "artist": "Tiny Moving Parts",
        },
        timestamp=4000000000,
    )
    save_album_details(
        db,
        {
            "name": "The Fall of Math",
            "artist": "65daysofstatic",
        },
        timestamp=3999999999,
    )
    save_album_details(
        db,
        {
            "name": "Next",
            "artist": "Trying Science",
        },
        timestamp=4000000001,
    )

    albums = list(fetch_albums_to_update(db, cutoff=4000000000))

    assert len(albums) == 1
    assert albums[0]["name"] == "The Fall of Math"


@pytest.mark.usefixtures("db_with_album_listens")
def test_accepts_a_limit(db):
    albums = list(fetch_albums_to_update(db, limit=2))

    assert len(albums) == 2
    assert albums[0]["name"] == "Tiny Moving Parts"
    assert albums[1]["name"] == "Next"
