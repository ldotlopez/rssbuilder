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


import hashlib
import logging
from pathlib import Path
from time import localtime, mktime

LOGGER = logging.getLogger(__name__)


class Cache:
    def __init__(self, base_dir: Path, delta: float = 60 * 60 * 2):
        self.base = base_dir
        self.delta = delta

    def _calc_filepath(self, id_: str) -> Path:
        h = hashlib.sha256(id_.encode("utf-8")).hexdigest()
        return self.base / h[0] / h[0:2] / h

    def get(self, url: str) -> bytes:
        filepath = self._calc_filepath(url)

        try:
            mtime = filepath.stat().st_mtime
        except FileNotFoundError:
            LOGGER.debug(f"cache miss: {url}")
            raise MissError()

        diff = mktime(localtime()) - mtime
        if diff >= self.delta:
            LOGGER.debug(f"cache expired: {url}")
            raise MissError()

        ret = filepath.read_bytes()
        LOGGER.debug(f"cache hit: {url}")

        return ret

    def set(self, url: str, contents: bytes) -> None:
        filepath = self._calc_filepath(url)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        filepath.write_bytes(contents)
        LOGGER.debug(f"cache save: {url} ({len(contents)} bytes)")


class MissError(Exception):
    pass
