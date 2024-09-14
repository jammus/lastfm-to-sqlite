from sqlite_utils import Database


def create_indexes(db: Database):
    db["playlist"].create_index(["artist"], if_not_exists=True)
    db["playlist"].create_index(["artist", "song"], if_not_exists=True)
    db["playlist"].create_index(["artist", "album"], if_not_exists=True)
    db["playlist"].create_index(["uts_timestamp"], if_not_exists=True)


def create_artist_view(db: Database):
    return db.create_view(
        "v_artists",
        "select distinct artist as name from playlist",
        replace=True
    )


def create_track_view(db: Database):
    return db.create_view(
        "v_tracks",
        "select distinct artist, song as name from playlist",
        replace=True
    )


def create_album_view(db: Database):
    return db.create_view(
        "v_albums",
        "select distinct artist, album as name from playlist",
        replace=True
    )


def create_artist_detail_view(db: Database):
    return db.create_view(
            "v_artist_details",
            """
            select name,
                   min(uts_timestamp) as discovered,
                   max(uts_timestamp) as last_listened
                from v_artists
                join playlist on playlist.artist = name
                group by artist
            """,
            replace=True
            )


def create_track_detail_view(db: Database):
    return db.create_view(
            "v_track_details",
            """
            select t.name, t.artist,
                   min(uts_timestamp) as discovered,
                   max(uts_timestamp) as last_listened
                from v_tracks as t
                join playlist on playlist.artist = t.artist and
                                 playlist.song = t.name
                group by t.artist, t.name
            """,
            replace=True
            )


def create_album_detail_view(db: Database):
    return db.create_view(
            "v_album_details",
            """
            select a.name, a.artist,
                   min(uts_timestamp) as discovered,
                   max(uts_timestamp) as last_listened
                from v_albums as a
                join playlist on playlist.artist = a.artist and
                                 playlist.album = a.name
                group by a.artist, a.name
            """,
            replace=True
            )


def create_all_views(db: Database):
    create_artist_view(db)
    create_artist_detail_view(db)

    create_track_view(db)
    create_track_detail_view(db)

    create_album_view(db)
    create_album_detail_view(db)
