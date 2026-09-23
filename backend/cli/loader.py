
import asyncio
import logging

from src.database import async_session_factory, init_db
from src.fetchers import TaskFetcher
from src.http import YandexClient
from src.parsers import ExamStructureParser, TaskParser
from src.repositories import JsonTaskRepository, SqlalchemyTaskRepository
from src.services import TaskLoaderService
from src.settings import Config, setup_logging

logger = logging.getLogger(__name__)


async def load_all_numbers(
    config: Config,
    service: TaskLoaderService,
) -> None:
    semaphore = asyncio.Semaphore(config.max_concurrency)

    async def load_number(number: int) -> None:
        async with semaphore:
            tasks = await service.load_by_number(number)

            path = config.output_file.format(number=number)
            JsonTaskRepository().save(tasks, path)
            logger.info(f"Сохранено {len(tasks)} заданий номера {number} в {path}")

            async with async_session_factory() as session:
                await SqlalchemyTaskRepository(session).save(tasks)
            logger.info(f"Сохранено {len(tasks)} заданий номера {number} в базу данных")

    numbers = range(config.min_task_number, config.max_task_number + 1)
    await asyncio.gather(*(load_number(n) for n in numbers))


async def main() -> None:
    config = Config()
    setup_logging(config.log_file)

    await init_db()
    logger.info("База данных инициализирована")

    client = YandexClient(config)
    try:
        service = TaskLoaderService(
            TaskFetcher(client, config),
            ExamStructureParser(),
            TaskParser(),
            config,
        )
        await load_all_numbers(config, service)
        logger.info("Загрузка всех заданий завершена")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
