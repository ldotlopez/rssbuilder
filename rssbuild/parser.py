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


from dataclasses import dataclass, field

import bs4

from .query import Query, get_one


@dataclass
class ParsedEntry:
    link: str
    title: str | None = None
    content: str | None = None
    image: str | None = None
    date: str | None = None


@dataclass
class ParsedBuffer:
    link: str = ""
    title: str | None = None
    description: str | None = None
    entries: list[ParsedEntry] = field(default_factory=lambda: [])


class Parser:
    def parse(
        self,
        buff: bytes,
        entries: str,
        link: Query | str,
        title: Query | str | None,
        content: Query | str | None,
        date: Query | str | None,
        image: Query | str | None,
    ) -> ParsedBuffer:
        def parse_entry(tag: bs4.Tag):
            if (link_ := get_one(tag, link)) is None:
                raise ValueError(tag)

            return ParsedEntry(
                link=link_,
                title=get_one(tag, title) if title else None,
                content=get_one(tag, content) if content else None,
                image=get_one(tag, image) if image else None,
                date=get_one(tag, date) if date else None,
            )

        soup = bs4.BeautifulSoup(buff, features="html.parser")

        link_q = Query(
            selector="head link", attributes={"rel": "canonical"}, target="href"
        )
        feed_link = get_one(soup, link_q) or ""

        feed_title = (get_one(soup, "head title") or "").strip()

        ret = ParsedBuffer(
            link=feed_link,
            title=feed_title,
            entries=[parse_entry(x) for x in soup.select(entries)],
        )

        return ret
