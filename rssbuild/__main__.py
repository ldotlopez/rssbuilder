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
from .fixers import CanonicalURLs, FeedFiller

logging.basicConfig()
logging.getLogger(NAME).setLevel(logging.DEBUG)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=Path)

    args = parser.parse_args()

    config = Config.from_filepath(args.config)

    for feed in config.feeds:
        buff = Fetcher().fetch(feed.url)
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

        print(Builder().build(data))


if __name__ == "__main__":
    main()
