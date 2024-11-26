import pytest
from sqlite_utils import Database

from lastfm import save_similar_artists
from lastfm.db_setup import create_similar_artists_table


@pytest.fixture
def db():
    database = Database(memory=True)
    create_similar_artists_table(database)
    return database


def test_persists_artists(db: Database):
    save_similar_artists(
        db,
        "Indoor Cities",
        [
            {"name": "He Was Eaten by Owls", "url": "http://Owls!"},
        ],
    )
    similar = list(db.query("select * from similar_artists"))
    assert len(similar) == 1
    assert similar[0]["id"] == "indoor cities"
    assert similar[0]["similar_id"] == "he was eaten by owls"


def test_saves_inferred_similar_position(db: Database):
    save_similar_artists(
        db,
        "He Was Eaten by Owls",
        [
            {"name": "Indoor Cities", "url": "http://cities"},
            {"name": "You Break, You Buy", "url": "http://buy"},
            {"name": "halfsleep", "url": "http://sleep"},
        ],
    )

    similar = list(db.query("select * from similar_artists order by position"))

    assert len(similar) == 3
    assert similar[0]["similar_id"] == "indoor cities"
    assert similar[0]["position"] == 1
    assert similar[1]["similar_id"] == "you break, you buy"
    assert similar[1]["position"] == 2
    assert similar[2]["similar_id"] == "halfsleep"
    assert similar[2]["position"] == 3


def test_overwrites_similar_artists_at_same_position(db: Database):
    save_similar_artists(
        db,
        "He Was Eaten by Owls",
        [
            {"name": "Indoor Cities", "url": "http://cities"},
            {"name": "You Break, You Buy", "url": "http://buy"},
            {"name": "halfsleep", "url": "http://sleep"},
        ],
    )

    save_similar_artists(
        db,
        "He Was Eaten by Owls",
        [
            {"name": "The Most", "url": "http://most"},
        ],
    )

    similar = list(db.query("select * from similar_artists order by position"))

    assert len(similar) == 3
    assert similar[0]["similar_id"] == "the most"
    assert similar[0]["position"] == 1
    assert similar[1]["similar_id"] == "you break, you buy"
    assert similar[1]["position"] == 2
    assert similar[2]["similar_id"] == "halfsleep"
    assert similar[2]["position"] == 3
