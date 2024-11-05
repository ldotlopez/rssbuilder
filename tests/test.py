import unittest
from pathlib import Path

from rssbuilder import Builder, Parser, Query
from rssbuilder.fixers import ALL as ALL_FIXERS
from rssbuilder.fixers import Fixer
from rssbuilder.parser import ParsedBuffer


def read_sample(name: str) -> bytes:
    return (Path(__file__).parent / "samples" / name).read_bytes()


class Engine:
    """
    Temporal class to figure out optimal implementation
    """

    def __init__(
        self,
        *,
        entries: str,
        link: Query | str,
        title: Query | str | None,
        content: Query | str | None,
        date: Query | str | None,
        image: Query | str | None,
    ):
        self.parser = Parser(
            entries=entries,
            link=link,
            title=title,
            content=content,
            date=date,
            image=image,
        )

    def buffer_as_rss(self, buffer: bytes) -> str:
        data = self.parser.parse(buffer)
        return Builder().build(data)


class Engine2:
    def __init__(
        self,
        parser: Parser,
        custom_fixers: list[type[Fixer]] | None = None,
        fixers: list[type[Fixer]] | None = None,
    ):
        self.fixers = fixers or ALL_FIXERS
        if custom_fixers:
            self.fixers.extend(custom_fixers)

        self.parser = parser

    def _parse(self, buffer) -> ParsedBuffer:
        data = self.parser.parse(buffer)
        return data
        # for FixerCls in ALL_FIXERS:
        #     FixerCls(feed).fix(data)

    def buffer_as_rss(self, buffer: bytes) -> str:
        data = self.parser.parse(buffer)
        return Builder().build(data)


class TestBuilder(unittest.TestCase):
    def test_engine2(self):
        tvcs = Engine2(
            parser=Parser(
                entries=".rss_item",
                link=Query(selector=".title a", target="href"),
                title=".title",
                image=Query(selector="amp-img", target="src"),
                content=".rss_content p",
                date=".rss_content small",
            )
        )
        rss = tvcs.buffer_as_rss(read_sample("tvcs.html"))
        self.assertEqual(len(rss), 4857)

    # def test_build(self):
    #     tvcs = Engine(
    #         entries=".rss_item",
    #         link=Query(selector=".title a", target="href"),
    #         title=".title",
    #         image=Query(selector="amp-img", target="src"),
    #         content=".rss_content p",
    #         date=".rss_content small",
    #     )
    #     rss = tvcs.buffer_as_rss(read_sample("tvcs.html"))
    #     self.assertEqual(len(rss), 4857)


if __name__ == "__main__":
    unittest.main()
