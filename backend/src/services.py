
import asyncio
import logging

from src.fetchers import KompegeFetcher, YandexTaskFetcher
from src.models import KompegeVariant, YandexExamTaskInfo, YandexTaskItem, YandexVariant
from src.parsers import (
    KompegeVariantParser,
    YandexExamStructureParser,
    YandexTaskParser,
    YandexVariantParser,
)
from src.settings import Config

logger = logging.getLogger(__name__)


class YandexTaskLoaderService:
    def __init__(
        self,
        fetcher: YandexTaskFetcher,
        structure_parser: YandexExamStructureParser,
        task_parser: YandexTaskParser,
        config: Config,
    ) -> None:
        self._fetcher = fetcher
        self._structure_parser = structure_parser
        self._task_parser = task_parser
        self._config = config

    async def load_by_number(self, number: int) -> list[YandexTaskItem]:
        info = await self._get_exam_task(number)

        logger.info(
            f"Задание {number} ({info.skill}): "
            f"{len(info.category_ids)} категорий"
        )

        return await self._load_tasks(info.category_ids)

    async def _get_exam_task(self, number: int) -> YandexExamTaskInfo:
        raw = await self._fetcher.fetch_exam_tasks()

        info = self._structure_parser.parse(raw).get(number)

        if info is None or not info.category_ids:
            raise LookupError(
                f"не найдены категории для задания номер {number}"
            )

        return info

    async def _load_tasks(
        self,
        category_ids: tuple[str],
    ) -> list[YandexTaskItem]:
        cfg = self._config

        first = await self._fetcher.fetch_page(
            1,
            cfg.page_size,
            list(category_ids),
        )

        pages = int(first.get("pages", 1))
        total = int(first.get("total", 0))

        logger.info(
            f"Всего {total} заданий на {pages} страницах"
        )

        tasks = self._parse_items(first)

        if pages > 0:
            logger.info(f"Загружена страница 1/{pages}")

        if pages > 1:
            tasks.extend(
                await self._load_remaining(
                    pages,
                    category_ids,
                )
            )

        tasks = self._remove_duplicates(tasks)

        if len(tasks) != total:
            logger.warning(
                f"Загружено {len(tasks)} заданий, "
                f"API сообщило о {total}"
            )

        return tasks

    async def _load_remaining(
        self,
        pages: int,
        category_ids: tuple[str],
    ) -> list[YandexTaskItem]:
        semaphore = asyncio.Semaphore(
            self._config.max_concurrency
        )

        async def fetch(page: int) -> list[YandexTaskItem]:
            async with semaphore:
                data = await self._fetcher.fetch_page(
                    page,
                    self._config.page_size,
                    list(category_ids),
                )

            logger.info(
                f"Загружена страница {page}/{pages}"
            )

            return self._parse_items(data)

        results = await asyncio.gather(
            *(fetch(page) for page in range(2, pages + 1)),
            return_exceptions=True,
        )

        tasks: list[YandexTaskItem] = []

        for page, result in zip(
            range(2, pages + 1),
            results,
        ):
            if isinstance(result, Exception):
                logger.error(
                    f"Ошибка при загрузке страницы {page}: {result}"
                )
                continue

            tasks.extend(result)

        return tasks

    def _parse_items(self, data: dict) -> list[YandexTaskItem]:
        return [
            self._task_parser.parse(item)
            for item in data.get("items", [])
        ]

    @staticmethod
    def _remove_duplicates(
        tasks: list[YandexTaskItem],
    ) -> list[YandexTaskItem]:
        seen: set[str] = set()
        unique: list[YandexTaskItem] = []

        for task in tasks:
            if task.task_id in seen:
                continue

            seen.add(task.task_id)
            unique.append(task)

        return unique


class YandexVariantSolverService:
    def __init__(
        self,
        fetcher: YandexTaskFetcher,
        parser: YandexVariantParser,
    ) -> None:
        self._fetcher = fetcher
        self._parser = parser

    async def solve(self, variant_id: str) -> YandexVariant:
        raw = await self._fetcher.fetch_variant(variant_id)

        variant = self._parser.parse(
            raw,
            variant_id,
        )

        logger.info(
            f"Получен вариант {variant_id}: "
            f"{len(variant.tasks)} заданий"
        )

        return variant


class KompegeVariantSolverService:
    def __init__(
        self,
        fetcher: KompegeFetcher,
        parser: KompegeVariantParser,
    ) -> None:
        self._fetcher = fetcher
        self._parser = parser

    async def solve(self, variant_id: str) -> KompegeVariant:
        raw = await self._fetcher.fetch_variant(variant_id)
        variant = self._parser.parse(raw)

        logger.info(
            f"Получен вариант {variant_id}: "
            f"{len(variant.tasks)} заданий"
        )

        return variant
