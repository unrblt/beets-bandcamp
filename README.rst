.. image:: http://img.shields.io/pypi/v/beets-bandcamp.svg
    :target: https://pypi.python.org/pypi/beets-bandcamp

Plugin for `beets <https://github.com/beetbox/beets>`_ to use bandcamp as an
autotagger source.

Installation
------------

Install this plugin with

..

   $ pip install beets-bandcamp

and add ``bandcamp`` to the ``plugins`` list in your beets config file.

Configuration
-------------

*
  **lyrics** If this is ``true`` the plugin will add lyrics to the tracks if
  they are available. Default is ``false``.

*
  **art** If this is ``true`` the plugin will add a source to the
  `FetchArt <http://beets.readthedocs.org/en/latest/plugins/fetchart.html>`_
  plugin to download album art for bandcamp albums (you need to enable the
  FetchArt plugin).  Default is ``false``.

*
  **split_artist_title** If this is ``true`` the plugin will try to split the
  title on `` - `` using the first part as artist and the rest as title.
  This can be useful for compilation albums, although you may still need to use
  the edit Candidates option of the
  `edit <https://beets.readthedocs.io/en/latest/plugins/edit.html>`_ plugin.
  Default is ``false``.

Usage
-----

This plugin uses the bandcamp URL as id (for both albums and songs). If no
matching release is found when importing you can select ``enter Id`` and paste
the bandcamp URL.
