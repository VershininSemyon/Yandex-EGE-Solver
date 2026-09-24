
import logging
from abc import ABC, abstractmethod

import aiohttp

from src.settings import Config

logger = logging.getLogger(__name__)


class HttpClient(ABC):
    @abstractmethod
    async def get(self, path: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def post(self, path: str, payload: list[dict]) -> dict:
        raise NotImplementedError


class YandexClient(HttpClient):
    def __init__(self, config: Config) -> None:
        self._config = config
        self._session: aiohttp.ClientSession | None = None
        self._csrf: str | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "user-agent": self._config.user_agent,
            "referer": self._config.referer,
            "origin": self._config.base_url,
        }

    async def _start_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                base_url=self._config.base_url,
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self._session

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _fetch_csrf(self) -> None:
        data = await self.get(self._config.csrf_path)
        self._csrf = data["sk"]
        logger.info("Получен CSRF-токен")

    async def get(self, path: str) -> dict:
        session = await self._start_session()
        async with session.get(path) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, path: str, payload: list[dict]) -> dict:
        if self._csrf is None:
            await self._fetch_csrf()

        session = await self._start_session()
        headers = {
            "x-csrf-token": self._csrf,
            "content-type": "application/json"
        }

        async with session.post(path, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()


class KompegeClient(HttpClient):
    async def get(self, path: str) -> dict:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=path)
            return await response.json()

    async def post(self, path: str, payload: list[dict]) -> dict:
        pass
