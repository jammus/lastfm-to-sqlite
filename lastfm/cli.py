# -*- coding: utf-8 -*-
import click
import requests
import datetime
from itertools import chain
from sqlite_utils import Database
from lastfm import LastFM, fetch_artist, fetch_artists_to_update, process_tracks_response, save_artist_details, save_love, save_recent_track
from lastfm.db_setup import create_indexes, create_all_tables


formats = [LastFM.DATE_FORMAT]


@click.group()
@click.version_option()
def cli():
    "Scrape LASTFM playlists to SQLite"


@cli.command("export")
@click.argument("api", type=click.STRING, required=True)
@click.argument(
    "database",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option("--user", type=click.STRING, required=True)
@click.option("--start_date", type=click.DateTime(formats))
@click.option("--end_date", type=click.DateTime(formats))
def export_playlist(
    api,
    database, 
    user, 
    start_date=None,
    end_date=None
):
    """
    Export user's lastfm playlist
    """        
    if not isinstance(database, Database):
        database = Database(database)

    create_all_tables(database)

    client: ApiClient = {
        "base_url": "https://ws.audioscrobbler.com/2.0",
        "api_key": api,
        "username": user,
        "session": requests.Session(),
    }

    api = LastFM(
        client=client,
        start_date=start_date,
        end_date=end_date
    )

    data = api.fetch_recent_tracks()
    with click.progressbar(length=0, label="Fetching recent tracks") as bar:
        for _, (page, metadata) in enumerate(data):
            bar.length = int(metadata["total"])
            for track in process_tracks_response(page):
                save_recent_track(database, track)
                bar.update(1)

    data = api.fetch_loved_tracks()
    with click.progressbar(length=0, label="Fetching loves") as bar:
        for _, (page, metadata) in enumerate(data):
            bar.length = int(metadata["total"])
            for love in process_tracks_response(page):
                save_love(database, love)
                bar.update(1)

    artists = fetch_artists_to_update(database, limit=1000)
    with click.progressbar(length=1000, label="Fetching artists") as bar:
        for _, artist in enumerate(artists):
            artist_details = fetch_artist(api.client, artist["name"])
            save_artist_details(database, artist_details,
                                timestamp=int(datetime.datetime.now().timestamp()))
            bar.update(1)

    create_indexes(database)

if __name__ == "__main__":
    cli()
