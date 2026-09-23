
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


def get_input_task_number(config: Config) -> int:
    while True:
        try:
            num = int(input(f"Введите номер задачи ({config.min_task_number}-{config.max_task_number}): "))

            if not (config.min_task_number <= num <= config.max_task_number):
                print("Неверный номер")
                continue

            return num
        except ValueError:
            print("Введите корректное число!")


async def main() -> None:
    config = Config()
    setup_logging(config.log_file)

    await init_db()
    logger.info("База данных инициализирована")

    number = get_input_task_number(config)
    client = YandexClient(config)

    try:
        service = TaskLoaderService(
            TaskFetcher(client, config),
            ExamStructureParser(),
            TaskParser(),
            config,
        )
        try:
            tasks = await service.load_by_number(number)
        except LookupError as exc:
            logger.error(f"{exc}")
            return

        path = config.output_file.format(number=number)
        JsonTaskRepository().save(tasks, path)
        logger.info(f"Сохранено {len(tasks)} заданий в {path}")

        async with async_session_factory() as session:
            await SqlalchemyTaskRepository(session).save(tasks)
        logger.info(f"Сохранено {len(tasks)} заданий в базу данных")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
