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


from feedgen.feed import FeedGenerator

from .parser import ParsedBuffer


class Builder:
    def build(self, data: ParsedBuffer) -> str:
        fg = FeedGenerator()
        fg.id(data.link)
        fg.link(href=data.link)
        fg.title(data.title)
        fg.description(data.description)

        # fg.id("http://lernfunk.de/media/654321")
        # fg.title("Some Testfeed")
        # fg.author({"name": "John Doe", "email": "john@example.de"})
        # fg.link(href="http://example.com", rel="alternate")
        # fg.logo("http://ex.com/logo.jpg")
        # fg.subtitle("This is a cool feed!")
        # fg.link(href="http://larskiesow.de/test.atom", rel="self")
        # fg.language("en")

        for entry in data.entries:
            fe = fg.add_entry()
            fe.id(entry.link)
            fe.link(href=entry.link)

            if entry.title:
                fe.title(entry.title)
            if entry.content:
                fe.content(entry.content)
            if entry.image:
                fe.enclosure(entry.image, type="image", length=0)

        # atomfeed = fg.atom_str(pretty=True)  # Get the ATOM feed as string
        rssfeed = fg.rss_str(pretty=True)  # Get the RSS feed as string

        return rssfeed.decode("utf-8")

        # fg.atom_file("atom.xml")  # Write the ATOM feed to a file
        # fg.rss_file("rss.xml")  # Write the RSS feed to a file
