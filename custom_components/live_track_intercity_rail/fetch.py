"""Reading a whole HTTP body, with a cap. No Home Assistant imports (tests load it).

! aiohttp's `StreamReader.read(n)` returns what has ARRIVED, up to n bytes -
not n bytes, and not the whole body. MEASURED on the box 2026-10-14 19:4xZ:
VIA's 320 KB train-status answer, read with `resp.content.read(4 MiB + 1)`,
came back as 152 KB three times in three, half a JSON document, so it never
decoded; the coordinator held the last answer for 10 minutes and then the
trains went unavailable, over and over through the day. Brightline's files
(1-3 KB) arrive in one piece, which is why it never showed there.
"""

from __future__ import annotations

CHUNK = 64 * 1024


async def read_capped(content, cap: int) -> bytes | None:
    """The WHOLE body, or None when it is larger than `cap` bytes."""
    buf = bytearray()
    async for chunk in content.iter_chunked(CHUNK):
        buf += chunk
        if len(buf) > cap:
            return None
    return bytes(buf)
