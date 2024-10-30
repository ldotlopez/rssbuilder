# Copyright (C) 2024- Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import argparse
import logging
from pathlib import Path
from pprint import pprint as pp

from . import NAME, Builder, Config, Fetcher, Parser
from .cache import Cache, MissError
from .fixers import CanonicalURLs, FeedFiller

logging.basicConfig()
logging.getLogger(NAME).setLevel(logging.WARNING)

import re


def slufigy(s: str) -> str:
    s_ = re.sub(r"[^a-z0-9]", "", s, flags=re.IGNORECASE).lower()
    if not s_:
        raise ValueError(s)

    return s_


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=Path)

    args = parser.parse_args()

    config = Config.from_filepath(args.config)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    cache = Cache(config.cache_dir)

    for feed in config.feeds:
        try:
            buff = cache.get(feed.url)
        except MissError:
            buff = Fetcher().fetch(feed.url)
            cache.set(feed.url, buff)

        data = Parser().parse(
            buff,
            entries=feed.queries.entries,
            link=feed.queries.link,
            title=feed.queries.title,
            image=feed.queries.image,
            content=feed.queries.content,
            date=feed.queries.date,
        )

        fixers = [FeedFiller(feed=feed), CanonicalURLs(feed=feed)]
        for fix in fixers:
            fix.fix(data)

        rss = Builder().build(data)

        output = config.output_dir / Path(f"{slufigy(feed.name)}.rss")
        output.write_text(rss)


if __name__ == "__main__":
    main()
