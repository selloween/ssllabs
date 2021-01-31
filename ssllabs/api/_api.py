import asyncio
import logging
from abc import ABC
from typing import KeysView, Optional

import httpx

API_VERSION = 3
SSLLABS_URL = f"https://api.ssllabs.com/api/v{API_VERSION}/"


class _Api(ABC):
    """Abstract class to communicate with Qualys SSL Labs Assessment APIs."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._client = client or httpx.AsyncClient()
        self._needs_closing = not bool(client)

    def __del__(self):
        if self._needs_closing:
            loop = asyncio.get_event_loop()
            loop.create_task(self._client.aclose())

    async def _call(self, api_endpoint: str, **kwargs) -> httpx.Response:
        """Invocate API."""
        r = await self._client.get(f"{SSLLABS_URL}{api_endpoint}", params=kwargs)
        r.raise_for_status()
        return r

    def _verify_kwargs(self, given: KeysView, known: list):
        """Log warning, if an argument is unknown."""
        for arg in given:
            if arg not in known:
                self._logger.warning(
                    "Argument '%s' is not known by the SSL Labs API. It will be send, but the results might be unexpected.",
                    arg)
