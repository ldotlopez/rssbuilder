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


from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

import platformdirs
import pydantic
import yaml

from .consts import NAME

LOGGER = logging.getLogger(__name__)

try:
    YAML_LOADER = yaml.CLoader
except AttributeError:
    YAML_LOADER = yaml.Loader


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    feeds: list[Feed] = []
    output_dir: Path
    cache_dir: Path = Path(platformdirs.user_cache_path(NAME))

    @staticmethod
    def _resolve_path(base: Path, rel: Path) -> Path:
        ret = rel.expanduser()
        if not ret.is_absolute():
            ret = base.parent / ret

        return ret

    @classmethod
    def from_filepath(cls, filepath: Path):
        with filepath.open("rt") as fh:
            data = yaml.load(fh, Loader=YAML_LOADER)
            self = Config(**data)

        self.output_dir = cls._resolve_path(filepath, self.output_dir)
        self.cache_dir = cls._resolve_path(filepath, self.cache_dir)

        return self


class Feed(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    url: str
    name: str
    description: str | None = None
    queries: Queries
    title: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def description_validator(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["description"] = data.get("description") or data["name"]
            data["title"] = data.get("title") or data["name"]

        return data


class Queries(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    entries: str
    link: Query
    title: Query | None = None
    content: Query | None = None
    date: Query | None = None
    image: Query | None = None


class Query(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    selector: str
    attributes: dict[str, str] | None = None
    target: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def coerce_model(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"selector": data}

        return data


def main():
    test_yaml = """
feeds:
  - url: https://www.tvcs.tv/noticies/
    queries:
      entries: .rss_item
      link:
        selector: .title a
        attribute: href
      title: .title
      image:
        selector: amp-img
        attribute: src
      content: .rss_content p
      date: .rss_content small

"""

    data = yaml.load(io.StringIO(test_yaml), Loader=YAML_LOADER)
    config = Config(**data)
    print(config.model_dump_json())


if __name__ == "__main__":
    main()
