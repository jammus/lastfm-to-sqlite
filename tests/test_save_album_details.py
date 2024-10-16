import pytest
from sqlite_utils import Database
from lastfm import save_album_details
from lastfm.db_setup import create_album_table


@pytest.fixture
def db():
    database = Database(memory=True)
    create_album_table(database)
    return database


def test_persists_album_details(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }
    save_album_details(db, album)

    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )

    assert saved_album["name"] == "Elf Titled"
    assert saved_album["artist"] == "The Advantage"
    assert saved_album["image_id"] == "abcddefgh"
    assert saved_album["url"] == "https://Elf+Titled"


def test_save_album_upserts_album_details(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }

    save_album_details(db, album)
    save_album_details(
        db, album | {"image_id": "hgfjgth", "url": "https://last.fm/Elf+Titled"}
    )

    saved_albums = list(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )

    assert len(saved_albums) == 1

    assert saved_albums[0]["image_id"] == "hgfjgth"
    assert saved_albums[0]["url"] == "https://last.fm/Elf+Titled"


def test_save_album_does_not_overwrite_image_or_url_when_none_or_empty(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }

    save_album_details(db, album)
    save_album_details(db, album | {"image_id": "", "url": ""})
    save_album_details(db, album | {"image_id": None, "url": None})

    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )

    assert saved_album["image_id"] == "abcddefgh"
    assert saved_album["url"] == "https://Elf+Titled"


def test_sets_last_updated_to_supplied_timestamp(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }

    save_album_details(db, album, timestamp=123456789)
    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )
    assert saved_album["last_updated"] == 123456789

    save_album_details(db, album, timestamp=234567890)
    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )
    assert saved_album["last_updated"] == 234567890


def test_sets_last_updated_to_supplied_timestamp(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }

    save_album_details(db, album, timestamp=123456789)
    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )
    assert saved_album["last_updated"] == 123456789


def test_sets_id_and_artist_id_as_lowered_names(db: Database):
    album = {
        "name": "Elf Titled",
        "artist": "The Advantage",
        "url": "https://Elf+Titled",
        "image_id": "abcddefgh",
    }

    save_album_details(db, album, timestamp=123456789)
    saved_album = next(
        db.query(
            "select * from album_details where name = :name and artist = :artist",
            {"name": "Elf Titled", "artist": "The Advantage"},
        )
    )
    assert saved_album["id"] == "elf titled"
    assert saved_album["artist_id"] == "the advantage"


def test_saving_album_details_is_case_insensitive(db: Database):
    album = {
        "name": "Lava Land",
        "artist": "Piglet",
        "image_id": "abcddefgh",
    }
    save_album_details(db, album, timestamp=123456789)

    album = {
        "name": "lava land",
        "artist": "PiGlet",
        "image_id": "hijklmnop",
    }
    save_album_details(db, album, timestamp=123456789)

    saved_album = next(
        db.query(
            "select * from album_details where id = :id and artist_id = :artist_id",
            {"id": "lava land", "artist_id": "piglet"},
        )
    )
    assert saved_album["image_id"] == "hijklmnop"
