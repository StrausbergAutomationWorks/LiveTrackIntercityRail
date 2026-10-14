"""fetch.read_capped: the WHOLE body, never what happened to have arrived.

Measured on the box 2026-10-14: `resp.content.read(4 MiB + 1)` gave 152 KB of
VIA's 320 KB answer, three times in three, so it never decoded and VIA's
trains went unavailable every ten minutes or so through the day.
"""

import asyncio
import pathlib
import unittest

from _load import load

fetch = load("fetch")
COMP = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail"


class Content:
    """Stands in for aiohttp's StreamReader: the body arrives in pieces."""

    def __init__(self, pieces):
        self.pieces = pieces

    async def read(self, n=-1):  # what the old code called: only the FIRST piece
        return self.pieces[0] if self.pieces else b""

    async def _gen(self):
        for p in self.pieces:
            yield p

    def iter_chunked(self, n):
        return self._gen()


def run(coro):
    return asyncio.run(coro)


class ReadCapped(unittest.TestCase):
    def test_whole_body_in_pieces(self):
        body = b'{"1 (10-11)": {"lat": 52.8}, "2 (10-12)": {"lat": 49.9}}'
        pieces = [body[:20], body[20:41], body[41:]]
        self.assertEqual(run(fetch.read_capped(Content(pieces), 1024)), body)

    def test_the_old_read_would_have_truncated(self):
        # The regression this module exists for: one piece is not the body.
        pieces = [b"x" * 152_492, b"y" * 167_715]
        got = run(fetch.read_capped(Content(pieces), 4 * 1024 * 1024))
        self.assertEqual(len(got), 320_207)

    def test_over_the_cap_is_refused(self):
        self.assertIsNone(run(fetch.read_capped(Content([b"a" * 10, b"b" * 10]), 15)))

    def test_exactly_the_cap_is_kept(self):
        self.assertEqual(run(fetch.read_capped(Content([b"a" * 15]), 15)), b"a" * 15)

    def test_empty_body(self):
        self.assertEqual(run(fetch.read_capped(Content([]), 15)), b"")

    def test_coordinator_no_longer_reads_a_partial_body(self):
        src = (COMP / "coordinator.py").read_text(encoding="utf-8")
        self.assertNotIn("await resp.content.read(", src)
        self.assertIn("read_capped(resp.content, RT_MAX_BYTES)", src)

    def test_a_failure_says_why(self):
        src = (COMP / "coordinator.py").read_text(encoding="utf-8")
        self.assertIn("last: {self._last_reason or 'no answer'}", src)
        self.assertIn("_LOGGER.warning(", src)


if __name__ == "__main__":
    unittest.main()
