import pytest
from sqlite_utils import Database

from lastfm import save_artist_tags
from lastfm.db_setup import create_artist_tags_table

@pytest.fixture
def db():
    database = Database(memory=True)
    create_artist_tags_table(database)
    return database


def test_persists_artist_tags(db: Database):
    save_artist_tags(db, "Melt-Banana", [
                                 {"name": "noise", "url": "http://noise"},
                                 {"name": "noise rock", "url": "http://noise+rock"},
                             ])
    tags = list(db.query("select * from artist_tags"))
    assert tags[0] == {"id": "melt-banana", "name": "noise", "url": "http://noise"}
    assert tags[1] == {"id": "melt-banana", "name": "noise rock",
                       "url": "http://noise+rock"}


def test_lower_cases_tags(db: Database):
    save_artist_tags(db, "Melt-Banana", [
                                 {"name": "NoiSe", "url": "http://noise"},
                                 {"name": "NOIse roCK", "url": "http://noise+rock"},
                             ])
    tags = list(db.query("select * from artist_tags"))
    assert tags[0] == {"id": "melt-banana", "name": "noise", "url": "http://noise"}
    assert tags[1] == {"id": "melt-banana", "name": "noise rock",
                       "url": "http://noise+rock"}
