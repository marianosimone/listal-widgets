from bs4 import BeautifulSoup
import urllib2
import re
from datetime import datetime


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


def _get_items(url):
    data = BeautifulSoup(urllib2.urlopen(url).read())
    items = data.rss.find_all('item')
    return [{
        'title': item.find('title').text,
        'image': _image_finder.search(item.find('description').text).groups()[0],
        'status': _statuses[item.find('listal:used').text],
        'since': item.find('pubdate').text
    } for item in items]


def _get_data(user, collection, ownership, status):
    base_url = 'http://%s.listal.com/rss/%s/%s/1?sortby=dateadded-desc'  # TODO: Handle paging

    items = []
    used_query = ('&used=%s' % _statuses[status] ) if status != 'all' else ''
    for s in _status[collection][ownership]:
        items.extend(_get_items((base_url % (user, collection, s)) + used_query))
    return items

def reading(user):
    return _get_data(user, 'books', 'all', 'using')
