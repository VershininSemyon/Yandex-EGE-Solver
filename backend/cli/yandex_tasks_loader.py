
import asyncio
import logging

from src.fetchers import YandexTaskFetcher
from src.http import YandexClient
from src.parsers import YandexExamStructureParser, YandexTaskParser
from src.repositories import JsonYandexTaskRepository
from src.services import YandexTaskLoaderService
from src.settings import Config, setup_logging

logger = logging.getLogger(__name__)


async def load_all_numbers(
    config: Config,
    service: YandexTaskLoaderService,
) -> None:
    semaphore = asyncio.Semaphore(config.max_concurrency)

    async def load_number(number: int) -> None:
        async with semaphore:
            tasks = await service.load_by_number(number)

            path = config.output_file.format(number=number)
            JsonYandexTaskRepository().save(tasks, path)
            logger.info(f"Сохранено {len(tasks)} заданий номера {number} в {path}")

    numbers = range(config.min_task_number, config.max_task_number + 1)
    await asyncio.gather(*(load_number(n) for n in numbers))


async def main() -> None:
    config = Config()
    setup_logging(config.log_file)

    client = YandexClient(config)
    try:
        service = YandexTaskLoaderService(
            YandexTaskFetcher(client, config),
            YandexExamStructureParser(),
            YandexTaskParser(),
            config,
        )
        await load_all_numbers(config, service)
        logger.info("Загрузка всех заданий завершена")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
