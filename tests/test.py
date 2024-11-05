import unittest
from pathlib import Path

from rssbuilder import Builder, Parser, Query
from rssbuilder.fixers import ALL as ALL_FIXERS
from rssbuilder.fixers import Fixer
from rssbuilder.models import FeedInfo
from rssbuilder.parser import ParsedBuffer


def read_sample(name: str) -> bytes:
    return (Path(__file__).parent / "samples" / name).read_bytes()


class Engine:
    """
    Temporal class to figure out optimal implementation
    """

    def __init__(
        self,
        feed_info: FeedInfo,
        parser: Parser,
        custom_fixers: list[type[Fixer]] | None = None,
        fixers: list[type[Fixer]] | None = None,
    ):
        self.feed_info = feed_info
        self.fixers = fixers or ALL_FIXERS
        if custom_fixers:
            self.fixers.extend(custom_fixers)

        self.parser = parser

    def _parse(self, buffer) -> ParsedBuffer:
        data = self.parser.parse(buffer)
        for FixerCls in ALL_FIXERS:
            FixerCls(self.feed_info).fix(data)  # type: ignore[abstract]

        return data

    def buffer_as_rss(self, buffer: bytes) -> str:
        return Builder().build(self._parse(buffer))


class TestBuilder(unittest.TestCase):
    def test_engine(self):
        tvcs = Engine(
            feed_info=FeedInfo(url="https://tvcs.com", name="TVCS"),
            parser=Parser(
                entries=".rss_item",
                link=Query(selector=".title a", target="href"),
                title=".title",
                image=Query(selector="amp-img", target="src"),
                content=".rss_content p",
                date=".rss_content small",
            ),
        )
        rss = tvcs.buffer_as_rss(read_sample("tvcs.html"))
        self.assertEqual(len(rss), 4841)


if __name__ == "__main__":
    unittest.main()
