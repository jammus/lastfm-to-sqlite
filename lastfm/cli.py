# -*- coding: utf-8 -*-
import click
from itertools import chain
from sqlite_utils import Database
from lastfm import LastFM, process_tracks_response


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
@click.option("-t", "--table", default="playlist", type=click.STRING)
@click.option("--user", type=click.STRING, required=True)
@click.option("--first_page", type=click.INT, default=1)
@click.option("--limit_per_page", type=click.INT, default=200)
@click.option("--extended", type=click.INT, default=0)
@click.option("--start_date", type=click.DateTime(formats))
@click.option("--end_date", type=click.DateTime(formats))
def export_playlist(
    api,
    database, 
    table, 
    user, 
    first_page=None, 
    limit_per_page=None,
    extended=None,
    start_date=None,
    end_date=None
):
    """
    Export user's lastfm playlist
    """        
    if not isinstance(database, Database):
        database = Database(database)

    tracks_table = database.table(table)
    loves_table = database.table("loves")
    api = LastFM(
        api=api, username=user, first_page=first_page, 
        limit_per_page=limit_per_page, extended=extended, 
        start_date=start_date, end_date=end_date
    )

    data = api.fetch_recent_tracks()
    first_page, metadata = next(data)
    with click.progressbar(length=int(metadata["total"]), label="Fetching recent tracks") as bar:
        for idx, (page, _) in enumerate(chain([(first_page, metadata)], data)):
            for recent_track in process_tracks_response(page):
                tracks_table.upsert(recent_track, pk="uts_timestamp")
                bar.update(1)

    data = api.fetch_loved_tracks()
    first_page, metadata = next(data)
    with click.progressbar(length=int(metadata["total"]), label="Fetching loves") as bar:
        for idx, (page, _) in enumerate(chain([(first_page, metadata)], data)):
            for recent_track in process_tracks_response(page):
                loves_table.upsert(recent_track, pk="uts_timestamp")
                bar.update(1)

if __name__ == "__main__":
    cli()
