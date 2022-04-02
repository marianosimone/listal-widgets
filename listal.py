from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from collections import namedtuple


_STATUSES = {
    "books": {
        "Using": "Reading",
        "Yes": "Read",
        "No": "Unread",
    },
}

ListalSourceConfig = namedtuple(
    "ListalSourceConfig", ["item_type", "status", "sources"]
)
ReadingBooks = ListalSourceConfig(
    **{
        "item_type": "books",
        "status": "Reading",
        "sources": ("owned", "wanted", "read"),
    }
)
ReadBooks = ListalSourceConfig(
    **{"item_type": "books", "status": "Read", "sources": ("read",)}
)

_image_finder = re.compile(r"img src='(.*)'")
flat_map = lambda f, xs: [y for ys in xs for y in f(ys)]


def guess_attributes(item, status_map):
    return {
        "title": item.find("title").text,
        "image": _image_finder.search(item.find("description").text).groups()[0],
        "status": status_map[item.find("listal:used").text],
        "published": item.find(
            "pubDate"
        ).text,  # Beware, if dealing with Movies, this is when the item was added
        "url": item.find("link").text,
    }


def _get_items(user, source_config):
    base_url = (
        "https://%s.listal.com/rss/%s/%s/1?sortby=dateadded-desc"  # TODO: Handle paging
    )
    source_urls = map(
        lambda ownership: base_url % (user, source_config.item_type, ownership),
        source_config.sources,
    )
    items = flat_map(
        lambda url: BeautifulSoup(urlopen(url).read(), "lxml-xml").rss.find_all("item"),
        source_urls,
    )
    status_map = _STATUSES[source_config.item_type]
    return [guess_attributes(item, status_map) for item in items]


def _get_data(user, source_config):
    items = _get_items(user, source_config)
    return [item for item in items if item["status"] == source_config.status]


def reading(user):
    return _get_data(user, ReadingBooks)


def read(user):
    return _get_data(user, ReadBooks)


def _extract_list_element_data(row):
    image, content = row.find_all("div", recursive=False)
    first, second = content.find_all("div", recursive=False)
    return {
        "image": image.find("img")["src"],
        "title": first.find("a").text,
        "url": first.find("a")["href"],
        "comment": second.find("div").decode_contents(formatter="html"),
    }


def list_details(name):
    data = BeautifulSoup(urlopen("https://www.listal.com/list/%s" % name).read())
    rows = data.body.find_all(attrs={"class": "notesrow"})
    return [_extract_list_element_data(row) for row in rows]
