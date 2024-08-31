import hashlib
import logging
from pathlib import Path
from time import localtime, mktime

LOGGER = logging.getLogger(__name__)

from .consts import NAME


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
            LOGGER.debug(f"cache hit: {url}")
        except FileNotFoundError:
            LOGGER.debug(f"cache miss: {url}")
            raise MissError()

        diff = mktime(localtime()) - mtime
        if diff >= self.delta:
            LOGGER.debug(f"cache expired: {url}")
            raise MissError()

        return filepath.read_bytes()

    def set(self, url: str, contents: bytes) -> None:
        filepath = self._calc_filepath(url)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        filepath.write_bytes(contents)
        LOGGER.debug(f"cache save: {url} ({len(contents)} bytes)")


class MissError(Exception):
    pass
