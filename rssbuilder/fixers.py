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


import abc

from .models import FeedInfo
from .parser import ParsedBuffer


class Fixer:
    def __init__(self, feed_info: FeedInfo):
        self.feed_info = feed_info

    @abc.abstractmethod
    def fix(self, data: ParsedBuffer):
        pass


class CanonicalURLs(Fixer):
    def fix(self, data: ParsedBuffer):
        data.link = data.link or self.feed_info.url

        for entry in data.entries:
            entry.link = self.as_canonical(entry.link)
            if entry.image:
                entry.image = self.as_canonical(entry.image)

    def build_url(self, partial_url: str) -> str:
        return self.feed_info.url.rstrip("/") + "/" + partial_url.lstrip("/")

    def as_canonical(self, url: str) -> str:
        if url[0] == "/":
            return self.build_url(url)

        return url


class FeedFiller(Fixer):
    def fix(self, data: ParsedBuffer):
        data.title = data.title or self.feed_info.title
        data.description = data.description or self.feed_info.description


ALL = [FeedFiller, CanonicalURLs]
