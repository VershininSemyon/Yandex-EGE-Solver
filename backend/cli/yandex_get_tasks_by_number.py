
import asyncio
import logging

from src.fetchers import YandexTaskFetcher
from src.http import YandexClient
from src.parsers import YandexExamStructureParser, YandexTaskParser
from src.repositories import JsonYandexTaskRepository
from src.services import YandexTaskLoaderService
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

    number = get_input_task_number(config)
    client = YandexClient(config)

    try:
        service = YandexTaskLoaderService(
            YandexTaskFetcher(client, config),
            YandexExamStructureParser(),
            YandexTaskParser(),
            config,
        )
        try:
            tasks = await service.load_by_number(number)
        except LookupError as exc:
            logger.error(f"{exc}")
            return

        path = config.output_file.format(number=number)
        JsonYandexTaskRepository().save(tasks, path)
        logger.info(f"Сохранено {len(tasks)} заданий в {path}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
