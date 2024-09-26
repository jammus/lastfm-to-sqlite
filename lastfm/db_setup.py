from sqlite_utils import Database


def create_indexes(db: Database):
    db["playlist"].create_index(["artist"], if_not_exists=True)
    db["playlist"].create_index(["artist", "song"], if_not_exists=True)
    db["playlist"].create_index(["artist", "album"], if_not_exists=True)
    db["playlist"].create_index(["uts_timestamp"], if_not_exists=True)


def create_artist_table(db: Database):
    db["artist_details"].create({
        "name": str,
        "discovered": int,
        "last_listened": int,
    }, pk="name", if_not_exists=True)


def create_track_table(db: Database):
    db["track_details"].create({
        "name": str,
        "artist": str,
        "discovered": int,
        "last_listened": int,
    }, pk=["name", "artist"], if_not_exists=True)


def create_album_table(db: Database):
    db["album_details"].create({
        "name": str,
        "artist": str,
        "discovered": int,
        "last_listened": int,
    }, pk=["name", "artist"], if_not_exists=True)


def create_all_tables(db: Database):
    create_artist_table(db)
    create_track_table(db)
    create_album_table(db)
