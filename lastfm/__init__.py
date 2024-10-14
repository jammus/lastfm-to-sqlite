# -*- coding: utf-8 -*-
import datetime
from typing import TypedDict
import requests
import re
from sqlite_utils import Database
from time import sleep


class ApiClient(TypedDict):
    base_url: str
    api_key: str
    session: requests.Session
    username: str


class LastFM:
    """Base LastFM class."""


    def __init__(
        self,
        client: ApiClient,
        start_date=None,
        end_date=None,
    ):
        self.client = client

        self.start_date = convert_to_timestamp(start_date)
        self.end_date = convert_to_timestamp(end_date)

    def fetch_recent_tracks(self):
        """Fetch user's track history given the parametrs."""
        yield from fetch_pages(self.client,
                               "user.getrecenttracks",
                               params={
                                 "from": self.start_date,
                                 "to": self.end_date,
                                 "extended": 1,
                               })


def fetch_loved_tracks(client: ApiClient):
    data = fetch_pages(client, "user.getlovedtracks")
    for _, (loves, metadata) in enumerate(data):
        for love in process_tracks_response(loves):
            yield love, metadata


DATE_FORMAT = "%Y-%m-%d"
def convert_to_timestamp(date):
    """Convert human-readable `date` - either `datetime.date` or `str` - to
    Unix Timestamp."""
    if date is None:
        return None
    if isinstance(date, datetime.date):
        return int(date.timestamp())
    return int(datetime.datetime.strptime(date, DATE_FORMAT).timestamp())


def fetch_artist(client: ApiClient, name, params=None):
    params = params or {}
    response = fetch_page(client, "artist.getinfo",
                          params={"artist": name, "autocorrect": "0"} | params)
    artist = response.get("artist", {})
    return {
        "name": artist.get("name", ""),
        "url": artist.get("url", ""),
        "image_id": extract_image_id(artist)
    }


def fetch_album(client: ApiClient, name: str, artist: str):
    response = fetch_page(client, "album.getinfo",
                          params={"album": name,
                                  "artist": artist,
                                  "autocorrect": 0})
    album = response.get("album", {})
    return {
        "name": album.get("name", ""),
        "artist": album.get("artist", ""),
        "url": album.get("url", ""),
        "image_id": extract_image_id(album)
    }


def fetch_pages(client: ApiClient, method, params=None, wait=0):
    page = 1
    params = params or {}
    while True:
        sleep(wait)
        content = fetch_page(client, method, { "page": page, "limit": 200 } | params)
        root_name = next(iter(content.keys()), "")
        root = content.get(root_name, {})
        item_name = next((key for key in root.keys() if key != "@attr"), "")
        metadata = root.get("@attr", {})
        data = root.get(item_name, None)
        yield data, metadata
        total_pages = int(metadata.get("totalPages", 0))
        page += 1
        if (page > total_pages):
            break


def fetch_page(client: ApiClient, method, params=None):
    params = params or {}
    default_params = {
        "api_key": client["api_key"],
        "method": method,
        "user": client["username"],
        "extended": 1,
        "format": "json",
    }
    tries = 0
    while True:
        tries += 1
        response = client["session"].get(client["base_url"], params=(params | default_params))
        if response.status_code == 200 or tries >= 5:
            break
    response.raise_for_status()
    return response.json()


def process_tracks_response(page):
    """Yield specific k:v items of each song within page."""
    if not page:
        yield None
    for song in page:
        if song.get("@attr", {}).get("nowplaying"):
            continue
        date = song.get("date", None)
        item = {
            "artist": song.get("artist", {}).get("name", None) or \
                        song.get("artist", {}).get("#text", ""),
            "song": song.get("name", None),
            "uts_timestamp": int(date["uts"]) if date else "",
            "datetime": date["#text"] if date else "",
            "image_id": extract_image_id(song)
        }
        album = song.get("album", {}).get("#text", None)
        if album is not None:
            item["album"] = album
        yield item


def extract_image_id(item):
    images = item.get("image", [])
    image = images[0].get("#text", "") if images else ""
    match = re.search(r"https?://.*/(?P<id>[^/.]*)\.", image)
    return match.group("id") if match else None


def save_recent_track(db: Database, recent_track):
    scrobble_columns = ("artist", "song", "album", "uts_timestamp", "datetime")
    db["playlist"].upsert(
            { k: v for k, v in recent_track.items() if k in scrobble_columns },
            pk="uts_timestamp")
    save_artist_listen_date(db, recent_track)
    save_track_listen_date(db, recent_track)
    save_track_details(db, recent_track)
    save_album_listen_date(db, recent_track)


def save_love(db: Database, love):
    love_column = ("artist", "song", "uts_timestamp", "datetime")
    db["loves"].upsert(
            { k: v for k, v in love.items() if k in love_column },
            pk="uts_timestamp")


def save_artist_listen_date(db: Database, artist_listen):
    db.execute(
        "insert into artist_details (id, name, discovered, last_listened)"
        "values (lower(:artist), :artist, :uts_timestamp, :uts_timestamp)"
            "on conflict(id)"
            "do update set discovered = min(:uts_timestamp, discovered),"
                          "last_listened = max(:uts_timestamp, last_listened)",
        artist_listen
    )


def save_artist_details(db: Database, artist_details, timestamp=None):
    with db.conn:
        db.execute((
            "insert into artist_details (id, name, image_id, url, last_updated)"
            "values (lower(:name), :name, :image_id, :url, :timestamp)"
                "on conflict(id)"
             "do update set image_id ="
                 "case when ifnull(:image_id, '') = '' then "
                     "image_id else :image_id end,"
                 "url ="
                 "case when ifnull(:url, '') = '' then "
                     "url else :url end,"
                 "last_updated = :timestamp"),
                   { "timestamp": timestamp, "image_id": None, "url": None } | artist_details
        )


def save_album_details(db: Database, album_details, timestamp=None):
    with db.conn:
        db.execute(
            ("insert into album_details (id, artist_id, name, artist, image_id, url, last_updated)"
             "values (lower(:name), lower(:artist), :name, :artist, :image_id, :url, :timestamp)"
             "on conflict(id, artist_id)"
             "do update set image_id ="
                 "case when ifnull(:image_id, '') = '' then "
                     "image_id else :image_id end,"
                 "url ="
                 "case when ifnull(:url, '') = '' then "
                     "url else :url end,"
                 "last_updated = :timestamp"),
            { "image_id": None, "url": None, "timestamp": timestamp } | album_details)


def fetch_artists_to_update(db: Database, cutoff=99999999999, limit=None):
    query = (
        "select * from artist_details "
            "where last_updated < :cutoff "
            "order by (last_updated - last_listened) asc"
    )

    if limit:
        query += " limit :limit"

    return db.query(
        query,
        { "cutoff": cutoff, "limit": limit }
    )


def save_track_listen_date(db, recent_track):
    db.execute(
        "insert into track_details (name, artist, discovered, last_listened)"
        "values (:song, :artist, :uts_timestamp, :uts_timestamp)"
            "on conflict(name, artist)"
            "do update set discovered = min(:uts_timestamp, discovered),"
                          "last_listened = max(:uts_timestamp, last_listened)",
        recent_track
    )


def save_track_details(db: Database, recent_track):
    if recent_track.get("image_id", None):
        db.execute(
            "insert into track_details (name, artist, image_id)"
            "values (:song, :artist, :image_id)"
                "on conflict(name, artist)"
                "do update set image_id = :image_id",
            recent_track
        )


def save_album_listen_date(db: Database, recent_track):
    if recent_track.get("album", None):
        db.execute(
            "insert into album_details (id, artist_id, name, artist, discovered, last_listened)"
            "values (lower(:album), lower(:artist), :album, :artist, :uts_timestamp, :uts_timestamp)"
                "on conflict(id, artist_id)"
                "do update set discovered = min(:uts_timestamp, discovered),"
                              "last_listened = max(:uts_timestamp, last_listened)",
            recent_track
    )
