from datasette import hookimpl


BASE_URL = "https://lastfm.freetls.fastly.net/i/u/"


def image_url(item, size="_"):
    image_id = item["image_id"] or "2a96cbd8b46e442fc41c2b86b821562f"
    return BASE_URL + size + "/" + image_id + ".webp"


@hookimpl
def extra_template_vars():
    return {
        "image_url": image_url,
    }
