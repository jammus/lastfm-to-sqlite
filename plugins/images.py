from datasette import hookimpl


BASE_URL = "https://lastfm.freetls.fastly.net/i/u/"


def image_url(item, size="_"):
    return BASE_URL + size + "/" + item["image_id"] + ".webp"


@hookimpl
def extra_template_vars():
    return {
        "image_url": image_url,
    }
