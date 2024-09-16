from datasette import hookimpl
from datetime import datetime


def current_date():
    return datetime.now()


def start_of_year(year):
    return datetime(year, 1, 1).timestamp()


def end_of_year(year):
    return datetime(year + 1, 1, 1).timestamp()


@hookimpl
def extra_template_vars():
    return {
        "current_date": current_date,
        "start_of_year": start_of_year,
        "end_of_year": end_of_year,
    }
