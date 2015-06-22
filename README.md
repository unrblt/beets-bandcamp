# beets-bandcamp

Plugin for [beets](https://github.com/sampsyo/beets) to use bandcamp as an
autotagger source.

## Usage

1. Install dependencies
```
$ pip install requests beautifulsoup4 isodate
```
2. Clone this project, or download [bandcamp.py](https://github.com/ageorge/beets-bandcamp/beetsplug/bandcamp.py),
   in to your configured pluginpath (e.g., `~/.beets`)
3. Add `bandcamp` to your configured beets plugins

## Configuration

* **``lyrics``** If this is `true` the plugin will add lyrics to the tracks if 
  they are available. Default is `false`.

* **``art``** If this is `true` the plugin will add a source to the
  [FetchArt](http://beets.readthedocs.org/en/latest/plugins/fetchart.html)
  plugin to download album art for bandcamp albums (you need to enable the
  [FetchArt](http://beets.readthedocs.org/en/latest/plugins/fetchart.html)
  plugin).  Default is `false`.
