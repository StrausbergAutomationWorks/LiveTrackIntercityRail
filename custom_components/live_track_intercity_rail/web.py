"""Serves the integration's marker pictures (pictures.py).

The Live Track Ships pattern (its web.py): the pictures ship INSIDE the
component and reach the map as `entity_picture`, which LiveTrackMapCard draws
bare (06_MAP_CONTRACT.md D4a-picture). Fixed files, read once and kept.
"""

from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from . import pictures

_LOGGER = logging.getLogger(__name__)


class PictureView(HomeAssistantView):
    """Return one picture."""

    url = pictures.URL_BASE + "/{name}.svg"
    name = "api:live_track_intercity_rail:picture"

    # ! An <img> (and a CSS background) cannot send an Authorization header, so
    # a picture URL must be reachable without one. The response is our own
    # artwork with no user data in it.
    requires_auth = False

    def __init__(self) -> None:
        self._cache: dict[str, bytes] = {}

    async def get(self, request: web.Request, name: str) -> web.Response:
        path = pictures.path(name)
        if path is None:
            return web.Response(status=404, text="unknown picture")
        body = self._cache.get(name)
        if body is None:
            try:
                body = await request.app["hass"].async_add_executor_job(path.read_bytes)
            except OSError:
                _LOGGER.exception("Could not read %s", path.name)
                return web.Response(status=500, text="read failed")
            self._cache[name] = body
        return web.Response(
            body=body,
            content_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400, immutable"},
        )


def register(hass: HomeAssistant) -> None:
    """Once per Home Assistant run; a second config entry must not register
    the route again."""
    key = f"{pictures.URL_BASE}_registered"
    if hass.data.get(key):
        return
    hass.http.register_view(PictureView())
    hass.data[key] = True
