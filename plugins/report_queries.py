from datasette import hookimpl
from datasette.app import Datasette


def fetch_top_artists(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
            select
              v.name, v.image_id, count(1) as listens, discovered,
              (discovered >= cast(:start as integer)) as new
            from
              playlist as p
            join
              artist_details as v on lower(p.artist) = v.id
            join
              artist_history as h on lower(p.artist) = h.id
            where
              uts_timestamp >= :start and
              uts_timestamp < :end 
            group by
              p.artist
            order by
              listens desc
            limit 20
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_top_albums(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
            select
              p.artist, p.album as name, image_id, count(1) as listens, discovered,
              (discovered >= cast(:start as integer)) as new
            from
              playlist as p
            join
              album_details as v on p.album = v.name
              and p.artist = v.artist
            where
              uts_timestamp >= :start and
              uts_timestamp < :end 
            group by
              p.artist, p.album
            order by
              listens desc
            limit 20
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_top_tracks(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
            select
              p.artist, name, v.image_id, count(1) as listens, discovered,
              (discovered >= cast(:start as integer)) as new
            from
              playlist as p
            join
              track_details as v on p.song = v.name
                                      and p.artist = v.artist
            where
              uts_timestamp >= :start and
              uts_timestamp < :end 
            group by
              p.artist, p.song
            order by
              listens desc
            limit 20
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_blast_artists(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
          select
            *, (first_listen_this_period - previous_listen) as since,
               (first_listen_this_period - previous_listen) / 60/60/24/365 as years
          from (
            select
              v.name, v.image_id, count(1) as past_listens,
              max(p1.uts_timestamp) as previous_listen, current_listens,
              first_listen_this_period
            from
              playlist as p1
            join (
                select
                  artist, count(1) as current_listens,
                  min(p2.uts_timestamp) as first_listen_this_period
                from
                  playlist as p2
                where
                  uts_timestamp >= :start and
                  uts_timestamp < :end 
                group by
                  artist
              ) as this_p
              on p1.artist = this_p.artist
            join 
              artist_details as v on v.id = lower(p1.artist)
            where
              p1.uts_timestamp < :start
            and
              current_listens > 5
            group by
            p1.artist
          )
          where
            since >= (365 * 24 * 60 * 60 * 2)
            and past_listens > 5
          order by
            (current_listens * years * years) desc
          limit 20
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_loves(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
            select
              p.artist, t.image_id, p.song as name, count(1) as listens
            from
              playlist as p
            join
              loves as l on l.artist = p.artist and l.song = p.song 
            join
              track_details as t on t.artist = p.artist and t.name = l.song
            where
              l.uts_timestamp >= :start and l.uts_timestamp < :end and
              p.uts_timestamp >= :start and p.uts_timestamp < :end
            group by
              p.artist, p.song
            order by
              listens desc
            limit 20
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_most_loved(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp:int):
        db = datasette.get_database()
        query = """
            select
              l.artist as name, count(1) as loves
            from
              loves as l
            where
              l.uts_timestamp >= :start and l.uts_timestamp < :end
            group by
              l.artist
            order by
              loves desc
            limit 1
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


def fetch_monthly_tags(datasette: Datasette):
    async def fetch(start_timestamp: int, end_timestamp: int):
        db = datasette.get_database()
        query = """
            select * from (select *, row_number() over (Partition by month order by freq desc) as rownum from (
              select
              t.name as tag, strftime ('%m', DATETIME(p.uts_timestamp, 'unixepoch')) month,
              count(1) as freq
            from
              playlist as p
              join artist_tags as t on t.id = lower(p.artist)
            where
              p.uts_timestamp >= :start
              and
              p.uts_timestamp < :end
              and
              tag not in ("seen live", "indie", "rock", "pop", "post rock", "electronic", "indie rock")
            group by
              t.name, month
            order by
              freq desc
              )) where rownum <= 5
        """
        return (await db.execute(
            query,
            {"start": start_timestamp, "end": end_timestamp})
        ).rows
    return fetch


@hookimpl
def extra_template_vars(datasette):
    return {
        "fetch_top_artists": fetch_top_artists(datasette),
        "fetch_top_albums": fetch_top_albums(datasette),
        "fetch_top_tracks": fetch_top_tracks(datasette),
        "fetch_blast_artists": fetch_blast_artists(datasette),
        "fetch_loves": fetch_loves(datasette),
        "fetch_most_loved": fetch_most_loved(datasette),
        "fetch_monthly_tags": fetch_monthly_tags(datasette),
    }
