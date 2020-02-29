from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


_image_finder = re.compile(r"img src='(.*)'")

_statuses = {
    'Yes': 'used',
    'Using': 'using',
    'No': 'unused',
    'used': 'Yes',
    'using': 'Using',
    'unused': 'No',
    '': 'unused'
}

_status = {
    'books': {
        'wanted': ('wanted',),
        'owned': ('owned',),
        'used': ('read',),
        'all': ('owned', 'wanted', 'read')
    },
    'movies': {
        'wanted': ('wanted',),
        'used': ('watched',),
        'all': ('wanted', 'watched')
    }
}


def guess_attributes(item):
    return {
        'title': item.find('title').text,
        'image': _image_finder.search(item.find('description').text).groups()[0],
        'status': _statuses[item.find('listal:used').text],
        'since': item.find('pubdate').text,
        'url': item.find('link').text,
    }


def _get_items(url):
    data = BeautifulSoup(urlopen(url).read(), "html.parser")
    items = data.rss.find_all('item')
    return [guess_attributes(item) for item in items]


def _get_data(user, collection, ownership, status):
    base_url = 'http://%s.listal.com/rss/%s/%s/1?sortby=dateadded-desc'  # TODO: Handle paging
    items = []
    used_query = ('&used=%s' % _statuses[status] ) if status != 'all' else ''
    for s in _status[collection][ownership]:
        items.extend(_get_items((base_url % (user, collection, s)) + used_query))
    return items

def reading(user):
    return _get_data(user, 'books', 'all', 'using')

def read(user):
    return _get_data(user, 'books', 'used', 'all')

def _extract_list_element_data(row):
    image, content = row.find_all('div', recursive=False)
    first, second = content.find_all('div', recursive=False)
    return {
        'image': image.find('img')['src'],
        'title': first.find('a').text,
        'url': first.find('a')['href'],
        'comment': second.find('div').decode_contents(formatter='html')
    }

def list_details(name):
    data = BeautifulSoup(urlopen('http://www.listal.com/list/%s' % name).read())
    rows = data.body.find_all(attrs={'class': 'notesrow'})
    return [_extract_list_element_data(row) for row in rows]
