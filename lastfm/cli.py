# -*- coding: utf-8 -*-
import click
from itertools import chain
from sqlite_utils import Database
from lastfm import LastFM, process_tracks_response, save_recent_track
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
@click.option("--first_page", type=click.INT, default=1)
@click.option("--limit_per_page", type=click.INT, default=200)
@click.option("--start_date", type=click.DateTime(formats))
@click.option("--end_date", type=click.DateTime(formats))
def export_playlist(
    api,
    database, 
    user, 
    first_page=None, 
    limit_per_page=None,
    start_date=None,
    end_date=None
):
    """
    Export user's lastfm playlist
    """        
    if not isinstance(database, Database):
        database = Database(database)

    create_all_tables(database)

    loves_table = database.table("loves")
    api = LastFM(
        api=api, username=user, first_page=first_page, 
        limit_per_page=limit_per_page,
        start_date=start_date, end_date=end_date
    )

    data = api.fetch_recent_tracks()
    first_page, metadata = next(data)
    with click.progressbar(length=int(metadata["total"]), label="Fetching recent tracks") as bar:
        for idx, (page, _) in enumerate(chain([(first_page, metadata)], data)):
            for track in process_tracks_response(page):
                save_recent_track(database, track)
                bar.update(1)

    data = api.fetch_loved_tracks()
    first_page, metadata = next(data)
    with click.progressbar(length=int(metadata["total"]), label="Fetching loves") as bar:
        for idx, (page, _) in enumerate(chain([(first_page, metadata)], data)):
            for love in process_tracks_response(page):
                loves_table.upsert(love, pk="uts_timestamp")
                bar.update(1)

    create_indexes(database)

if __name__ == "__main__":
    cli()
