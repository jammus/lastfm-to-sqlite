import pytest
from sqlite_utils import Database

from lastfm import fetch_artists_to_update, save_artist_details, save_artist_listen_date
from lastfm.db_setup import create_artist_table

@pytest.fixture
def db():
    database = Database(memory=True)
    create_artist_table(database)
    return database


def test_last_updated_date_defaults_to_zero(db):
    artist_listen = {
        "artist": "65daysofstatic",
        "uts_timestamp": 1234567890,
    }

    save_artist_listen_date(db, artist_listen)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["last_updated"] == 0


def test_saves_artist_with_id_as_lowered_name(db):
    save_artist_details(db, {"name": "The Cabs"}, timestamp=2345678901)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "The Cabs" }
    ))

    assert artist["id"] == "the cabs"

    save_artist_details(db, {"name": "Try Science"}, timestamp=3456789012)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "Try Science" }
    ))

    assert artist["id"] == "try science"


def test_does_not_overwrite_artist_names(db):
    # This is to work around the Last.fm API returning artist names with casing
    # that does not match the website. user.getrecenttracks seems to be a
    # better source, and because we're writing from there first we can keep the
    # first spelling encountered

    save_artist_details(db, {"name": "NYOS"}, timestamp=2345678901)
    save_artist_details(db, {"name": "Nyos"}, timestamp=3456789012)

    [artist] = list(db.query(
        "select * from artist_details where id = :id",
        { "id": "nyos" }
    ))

    assert artist["name"] == "NYOS"
    assert artist["last_updated"] == 3456789012


def test_last_updated_date_is_set_to_supplied_timestamp_on_save(db):
    save_artist_details(db, {"name": "65daysofstatic"}, timestamp=2345678901)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["last_updated"] == 2345678901

    save_artist_details(db, {"name": "65daysofstatic"}, timestamp=3456789012)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["last_updated"] == 3456789012


def test_sets_image_id_when_supplied(db):
    save_artist_details(db, {"name": "65daysofstatic", "image_id": "cabbage"}, timestamp=2345678901)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["image_id"] == "cabbage"

    save_artist_details(db, {"name": "65daysofstatic", "image_id": "badfaff"}, timestamp=3456789012)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["image_id"] == "badfaff"


def test_sets_url_when_supplied(db):
    save_artist_details(db, {"name": "65daysofstatic", "url":
                             "https://www.last.fm/music/65daysofstatic"}, timestamp=2345678901)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "65daysofstatic" }
    ))

    assert artist["url"] == "https://www.last.fm/music/65daysofstatic"

    save_artist_details(db, {"name": "Try Science", "url":
                             "https://www.last.fm/music/Try+Science"}, timestamp=3456789012)

    [artist] = list(db.query(
        "select * from artist_details where name = :artist",
        { "artist": "Try Science" }
    ))

    assert artist["url"] == "https://www.last.fm/music/Try+Science"
