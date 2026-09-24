
from src.http import HttpClient
from src.settings import (
    TYPE_GET_EXAM_TASKS,
    TYPE_GET_VARIANT,
    TYPE_TASK_LIST,
    Config,
)


class YandexTaskFetcher:
    def __init__(self, client: HttpClient, config: Config) -> None:
        self._client = client
        self._config = config

    async def gpttr(self, payload: list[dict]) -> dict:
        return await self._client.post(
            self._config.gpttr_path,
            payload,
        )

    async def fetch_exam_tasks(self) -> dict:
        payload = [
            {
                "type": TYPE_GET_EXAM_TASKS,
                "subject_id": self._config.subject_id,
            }
        ]

        return await self.gpttr(payload)

    async def fetch_page(
        self,
        page: int,
        size: int,
        category_ids: list[str],
    ) -> dict:
        payload = [
            {
                "type": TYPE_TASK_LIST,
                "subject_id": self._config.subject_id,
                "category_ids": list(category_ids),
                "order": [
                    ["difficulty_level", "ascending"],
                    ["dt_created", "descending"],
                ],
                "params": {
                    "page": page,
                    "size": size,
                },
                "use_linked": self._config.use_linked,
            }
        ]

        return await self.gpttr(payload)

    async def fetch_variant(self, variant_id: str) -> dict:
        payload = [
            {
                "type": TYPE_GET_VARIANT,
                "variant_id": variant_id,
            }
        ]

        return await self.gpttr(payload)


class KompegeFetcher:
    def __init__(self, client: HttpClient, config: Config) -> None:
        self._client = client
        self._config = config

    async def fetch_variant(self, variant_id: str) -> dict:
        return await self._client.get(path=f"{self._config.kompege_variants_url}/{variant_id}")
