# -*- coding: utf-8 -*-
import datetime
from typing import List
import requests
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
        first_page: int = 1,
        limit_per_page: int = 200,
        extended: int = 0,
        start_date=None,
        end_date=None,
    ):
        self.api = self._validate_apikey(api)
        self.username = username
        self.first_page = first_page
        self.limit_per_page = limit_per_page
        self.extended = extended
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
        yield from self.fetch_all_pages("user.getrecenttracks", "recenttracks",
                                        "track", limit=self.limit_per_page,
                                        page=self.first_page,
                                        params={
                                            "user": self.username,
                                            "from": self.start_date,
                                            "to": self.end_date,
                                            "extended": self.extended,
                                        })

    def fetch_loved_tracks(self):
        """Fetch user's loved tracks given the parametrs."""
        yield from self.fetch_all_pages("user.getlovedtracks", "lovedtracks",
                                        "track", limit=self.limit_per_page,
                                        page=self.first_page,
                                        params={
                                            "user": self.username,
                                        })

    def fetch_all_pages(self, method, root_name, item_name, page=1, limit=200, params=None):
        session = requests.Session()
        params["method"] = method
        params["page"] = page
        params["limit"] = limit
        params["api_key"] = self.api
        params["format"] = "json"
        while True:
            response = session.get(LastFM.URL, params=params).json()
            metadata = response[root_name]["@attr"]
            data = response[root_name][item_name]
            yield data, metadata
            total_pages = int(metadata["totalPages"])
            params["page"] += 1
            if (params["page"] > total_pages):
                break
            sleep(1)
        session.close()


def process_tracks_response(page):
    """Yield specific k:v items of each song within page."""
    for song in page:
        if song.get("@attr", {}).get("nowplaying"):
            continue
        date = song.get("date", None)
        album = song.get("album", {}).get("#text", None)
        item = {
            "artist": song.get("artist", {}).get("name", None) or \
                        song.get("artist", {}).get("#text", ""),
            "song": song.get("name", None),
            "uts_timestamp": int(date["uts"]) if date else "",
            "datetime": date["#text"] if date else "",
        }
        if album is not None:
            item["album"] = album
        yield item
