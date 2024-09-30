# -*- coding: utf-8 -*-
import datetime
import requests
from sqlite_utils import Database
from time import sleep


class APIError(Exception):
    """APIError is raised when provided key is invalid
    (should be 32 alphanum characters long)."""
    pass


class LastFM:
    """Base LastFM class."""

    URL = "http://ws.audioscrobbler.com/2.0"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        api: str,
        username: str,
        start_date=None,
        end_date=None,
    ):
        self.api = self._validate_apikey(api)
        self.username = username
        self.start_date = None
        self.end_date = None

        if start_date is not None:
            self.start_date = self._convert_to_timestamp(start_date)
        if end_date is not None:
            self.end_date = self._convert_to_timestamp(end_date)

    @staticmethod
    def _validate_apikey(api):
        """Ensure apikey is valid."""
        if api.isalnum() and len(api) == 32:
            return api
        raise APIError("API key should be 32 alphanum char. long.")

    @staticmethod
    def _convert_to_timestamp(date):
        """Convert human-readable `date` - either `datetime.date` or `str` - to
        Unix Timestamp."""
        if isinstance(date, datetime.date):
            return int(date.timestamp())
        return int(datetime.datetime.strptime(date, LastFM.DATE_FORMAT).timestamp())

    def fetch_recent_tracks(self):
        """Fetch user's track history given the parametrs."""
        yield from self.fetch_all_pages("user.getrecenttracks",
                                        params={
                                            "user": self.username,
                                            "from": self.start_date,
                                            "to": self.end_date,
                                            "extended": 1,
                                        })

    def fetch_loved_tracks(self):
        """Fetch user's loved tracks given the parametrs."""
        yield from self.fetch_all_pages("user.getlovedtracks",
                                        params={
                                            "user": self.username,
                                        })

    def fetch_all_pages(self, method, params=None):
        session = requests.Session()
        params["api_key"] = self.api
        yield from fetch_pages(session, method, params, wait=0.25)
        session.close()


def fetch_pages(session, method, params=None, wait=0):
    page = 1
    params = params or {}
    while True:
        sleep(wait)
        content = fetch_page(session, method, { "page": page, "limit": 200 } | params)
        root_name = next(iter(content.keys()), "")
        root = content.get(root_name, {})
        item_name = next((key for key in root.keys() if key != "@attr"), "")
        metadata = root.get("@attr", {})
        data = root.get(item_name, None)
        yield data, metadata
        total_pages = int(metadata["totalPages"])
        page += 1
        if (page > total_pages):
            break


def fetch_page(session, method, params=None):
    params = params or {}
    default_params = {
        "method": method,
        "format": "json",
    }
    tries = 0
    while True:
        tries += 1
        response = session.get(LastFM.URL, params=(params | default_params))
        if response.status_code == 200 or tries >= 5:
            break
    response.raise_for_status()
    return response.json()


def process_tracks_response(page):
    """Yield specific k:v items of each song within page."""
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
        }
        album = song.get("album", {}).get("#text", None)
        if album is not None:
            item["album"] = album
        yield item


def save_recent_track(db: Database, recent_track):
    db["playlist"].upsert(recent_track, pk="uts_timestamp")
    save_artist_listen_date(db, recent_track)
    save_track_listen_date(db, recent_track)
    save_album_listen_date(db, recent_track)


def save_artist_listen_date(db, recent_track):
    db.execute(
        "insert into artist_details (name, discovered, last_listened)"
        "values (:artist, :uts_timestamp, :uts_timestamp)"
            "on conflict(name)"
            "do update set discovered = min(:uts_timestamp, discovered),"
                          "last_listened = max(:uts_timestamp, last_listened)",
        recent_track
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


def save_album_listen_date(db, recent_track):
    if recent_track.get("album", None):
        db.execute(
            "insert into album_details (name, artist, discovered, last_listened)"
            "values (:album, :artist, :uts_timestamp, :uts_timestamp)"
                "on conflict(name, artist)"
                "do update set discovered = min(:uts_timestamp, discovered),"
                              "last_listened = max(:uts_timestamp, last_listened)",
            recent_track
    )


def save_track(db: Database, recent_track):
    track = { key: recent_track[key] for key in ["song", "artist"] }
    db["tracks"].upsert(track, pk=["artist", "song"])
