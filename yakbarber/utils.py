"""Utility functions for Yak Barber."""

import os
import re
import datetime
import time
from itertools import islice

import pytz
from bs4 import BeautifulSoup


def safe_mkdir(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def split_every(n, iterable):
    """Split an iterable into chunks of size n."""
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


def convert_http_to_https(url, web_root):
    """Convert http:// URLs to https:// if the site uses https."""
    if 'https://' in web_root:
        web_root_base = web_root.split('https://')[1]
        return re.sub(f'http://{web_root_base}', f'https://{web_root_base}', url)
    return url


def remove_punctuation(text):
    """Remove punctuation from text for use in filenames/URLs."""
    text = re.sub(r'\s[^a-zA-Z0-9]\s', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]+', '', text)
    text = text.encode('ascii', 'xmlcharrefreplace')
    text = text.decode('utf-8')
    return text


def extract_tags(html, tag):
    """Remove all instances of a given HTML tag from the content."""
    soup = BeautifulSoup(html, 'html.parser')
    to_extract = soup.findAll(tag)
    for item in to_extract:
        item.extract()
    return str(soup)


def strip_tags(html):
    """Strip all HTML tags, returning plain text."""
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def rfc3339_convert(time_string):
    """Convert a datetime string to RFC3339 format for Atom feeds."""
    strip = time.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    dt = datetime.datetime.fromtimestamp(time.mktime(strip))
    pacific = pytz.timezone('US/Pacific')
    ndt = dt.replace(tzinfo=pacific)
    utc = pytz.utc
    return ndt.astimezone(utc).isoformat().split('+')[0] + 'Z'
