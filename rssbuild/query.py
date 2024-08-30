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


import bs4

from .models import Query


def get_one(soup: bs4.Tag, query: Query | str) -> str | None:
    if results := get(soup, query):
        return results[0]

    if len(results) > 1:
        raise ValueError("Multiple values", results)

    return None


def get(soup: bs4.Tag, query: Query | str) -> list[str | None]:
    if isinstance(query, str):
        query = Query(selector=query)
    elif isinstance(query, Query):
        pass
    else:
        raise TypeError(query)

    tags = soup.select(query.selector)

    if query.attributes:
        tags = [tag for tag in tags if matches_attrs(tag, query.attributes)]

    if query.target:
        return [tag.attrs.get(query.target) for tag in tags]
    else:
        return [tag.text for tag in tags]


def matches_attrs(tag: bs4.Tag, attrs: dict[str, str]):
    for name, value in attrs.items():
        tag_values = tag.attrs.get(name)

        if not tag_values:
            return False

        elif isinstance(tag_values, str):
            tag_values = [tag_values]

        elif isinstance(tag_values, list):
            tag_values = tag_values

        else:
            raise ValueError(tag)

        if value not in tag_values:
            return False

    return True
