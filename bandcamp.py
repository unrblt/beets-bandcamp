#
# TODO:
#   - error handling / logging
#   - album_for_id
#   - track_for_id
#
"""Adds bandcamp album search support to the autotagger. Requires the
BeautifulSoup library.
"""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import beets.ui
from beets import logging
from beets.autotag.hooks import AlbumInfo, TrackInfo, Distance
from beets.plugins import BeetsPlugin
import beets
import requests
from bs4 import BeautifulSoup
import isodate


USER_AGENT = u'beets/{0} +http://beets.radbox.org/'.format(beets.__version__)
BANDCAMP_SEARCH = u'http://bandcamp.com/search?q='
BANDCAMP_ALBUM = u'album'
BANDCAMP_ARTIST = u'band'
BANDCAMP_TRACK = u'track'


class BandcampPlugin(BeetsPlugin):

    def __init__(self):
        super(BandcampPlugin, self).__init__()
        self.config.add({'source_weight': 0.5})

    def album_distance(self, items, album_info, mapping):
        """Returns the album distance.
        """
        dist = Distance()
        if album_info.data_source == 'bandcamp':
            dist.add('source', self.config['source_weight'].as_number())
        return dist

    def candidates(self, items, artist, album, va_likely):
        """Returns a list of AlbumInfo objects for bandcamp search results
        matching an album and artist (if not various).
        """
        return self.get_albums(album)

    def get_albums(self, query):
        """Returns a list of AlbumInfo objects for a discogs search query.
        """
        album_urls = self._search(query, BANDCAMP_ALBUM)
        return [self.get_album_info(url) for url in album_urls]

    def get_album_info(self, url):
        """Returns an AlbumInfo object for a bandcamp album page.
        """
        html = self._get(url)
        name_section = html.find(id='name-section')
        album = name_section.find(attrs={'itemprop': 'name'}).text.strip()
        # Even though there is an item_id in some urls in bandcamp, it's not
        # visible on the page and you can't search by the id, so we need to use
        # the url as id.
        album_id = url
        artist = name_section.find(attrs={'itemprop': 'byArtist'}) .text.strip()
        release = html.find('meta', attrs={'itemprop': 'datePublished'})['content']
        release = isodate.parse_date(release)
        artist_url = url.split('/album/')[0]
        tracks = []
        for row in html.find(id='track_table').find_all(attrs={'itemprop': 'tracks'}):
            track = self._parse_track(row)
            track.track_id = '{0}{1}'.format(artist_url, track.track_id)
            tracks.append(track)

        return AlbumInfo(album, album_id, artist, artist_url, tracks,
                         year=release.year, month=release.month,
                         day=release.day, country='XW', media='Digital Media',
                         data_source='bandcamp', data_url=url)

    def _search(self, query, type=BANDCAMP_ALBUM):
        """Returns a list of bandcamp urls form type items matching query.
        """
        if type not in [BANDCAMP_ARTIST, BANDCAMP_ALBUM, BANDCAMP_TRACK]:
            raise ValueError('Invalid type for search: %s' % type)

        results = self._get(BANDCAMP_SEARCH + query)
        clazz = u'searchresult %s' % type
        urls = []
        for result in results.find_all('li', attrs={'class': clazz}):
            a = result.find(attrs={'class': 'heading'}).a
            if a is not None:
                urls.append(a['href'].split('?')[0])

        return urls

    def _get(self, url):
        """Returns a BeautifulSoup object with the contents of url.
        """
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, headers=headers)
        return BeautifulSoup(r.text)

    def _parse_track(self, track_html):
        """Returns a TrackInfo derived from the html describing a track in a
        bandcamp album page.
        """
        track_num = track_html['rel'].split('=')[1]
        track_num = int(track_num)

        title_html = track_html.find(attrs={'class': 'title-col'})
        title = title_html.find(attrs={'itemprop': 'name'}).text.strip()
        track_id = title_html.find(attrs={'itemprop': 'url'})['href']
        try:
            duration = title_html.find('meta', attrs={'itemprop': 'duration'})['content']
            duration = duration.replace('P', 'PT')
            track_length = isodate.parse_duration(duration).total_seconds()
        except TypeError:
            track_length = None

        return TrackInfo(title, track_id, index=track_num, length=track_length)

