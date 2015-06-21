"""Adds bandcamp album search support to the autotagger. Requires the
BeautifulSoup library.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import beets.ui
from beets.autotag.hooks import AlbumInfo, TrackInfo, Distance
from beets.plugins import BeetsPlugin
import beets
import requests
from bs4 import BeautifulSoup
import isodate


USER_AGENT = u'beets/{0} +http://beets.radbox.org/'.format(beets.__version__)
BANDCAMP_SEARCH = u'http://bandcamp.com/search?q={query}&page={page}'
BANDCAMP_ALBUM = u'album'
BANDCAMP_ARTIST = u'band'
BANDCAMP_TRACK = u'track'


class BandcampPlugin(BeetsPlugin):

    def __init__(self):
        super(BandcampPlugin, self).__init__()
        self.config.add({
            'source_weight': 0.5,
            'min_candidates': 5,
        })

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

    def album_for_id(self, album_id):
        """Fetches an album by its bandcamp ID and returns an AlbumInfo object
        or None if the album is not found.
        """
        # We use album url as id, so we just need to fetch and parse the
        # album page.
        url = album_id
        return self.get_album_info(url)

    def item_candidates(self, item, artist, album):
        """Returns a list of TrackInfo objects from a bandcamp search matching
        a singleton.
        """
        if item.title:
            return self.get_tracks(item.title)
        if item.album:
            return self.get_tracks(item.album)
        if item.artist:
            return self.get_tracks(item.artist)
        return []

    def track_for_id(self, track_id):
        """Fetches a track by its bandcamp ID and returns a TrackInfo object
        or None if the track is not found.
        """
        url = track_id
        return self.get_track_info(url)

    def get_albums(self, query):
        """Returns a list of AlbumInfo objects for a bandcamp search query.
        """
        album_urls = self._search(query, BANDCAMP_ALBUM)
        return [self.get_album_info(url) for url in album_urls]

    def get_album_info(self, url):
        """Returns an AlbumInfo object for a bandcamp album page.
        """
        try:
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
                track = self._parse_album_track(row)
                track.track_id = '{0}{1}'.format(artist_url, track.track_id)
                tracks.append(track)

            return AlbumInfo(album, album_id, artist, artist_url, tracks,
                             year=release.year, month=release.month,
                             day=release.day, country='XW', media='Digital Media',
                             data_source='bandcamp', data_url=url)
        except requests.exceptions.RequestException as e:
            self._log.debug("Communication error while fetching album {0!r}: "
                            "{1}".format(url, e))

    def get_tracks(self, query):
        """Returns a list of TrackInfo objects for a bandcamp search query.
        """
        track_urls = self._search(query, BANDCAMP_TRACK)
        return [self.get_track_info(url) for url in track_urls]

    def get_track_info(self, url):
        """Returns a TrackInfo object for a bandcamp track page.
        """
        try:
            html = self._get(url)
            name_section = html.find(id='name-section')
            title = name_section.find(attrs={'itemprop': 'name'}).text.strip()
            artist_url = url.split('/track/')[0]
            artist = name_section.find(attrs={'itemprop': 'byArtist'}).text.strip()

            try:
                duration = html.find('meta', attrs={'itemprop': 'duration'})['content']
                track_length = float(duration)
                if track_length == 0:
                    track_length = None
            except TypeError:
                track_length = None

            return TrackInfo(title, url, length=track_length, artist=artist,
                             artist_id=artist_url, data_source='bandcamp',
                             media='Digital Media', data_url=url)
        except requests.exceptions.RequestException as e:
            self._log.debug("Communication error while fetching track {0!r}: "
                            "{1}".format(url, e))


    def _search(self, query, search_type=BANDCAMP_ALBUM, page=1):
        """Returns a list of bandcamp urls for items of type search_type
        matching the query.
        """
        if search_type not in [BANDCAMP_ARTIST, BANDCAMP_ALBUM, BANDCAMP_TRACK]:
            self._log.debug('Invalid type for search: {0}'.format(search_type))
            return None

        try:
            urls = []
            # Search bandcamp until min_candidates results have been found or
            # we hit the last page in the results.
            while len(urls) < self.config['min_candidates'].as_number():
                self._log.debug('Searching {}  page {}'.format(search_type, page))
                results = self._get(BANDCAMP_SEARCH.format(query=query, page=page))
                clazz = u'searchresult {0}'.format(search_type)
                for result in results.find_all('li', attrs={'class': clazz}):
                    a = result.find(attrs={'class': 'heading'}).a
                    if a is not None:
                        urls.append(a['href'].split('?')[0])

                # Stop searching if we are on the last page.
                if not results.find('a', attrs={'class': 'next'}):
                    break
                page += 1

            return urls
        except requests.exceptions.RequestException as e:
            self._log.debug("Communication error while searching page {0} for {1!r}: "
                            "{2}".format(page, query, e))
            return []

    def _get(self, url):
        """Returns a BeautifulSoup object with the contents of url.
        """
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return BeautifulSoup(r.text)

    def _parse_album_track(self, track_html):
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

