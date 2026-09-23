
import asyncio
import sys

from src.fetchers import TaskFetcher
from src.http import YandexClient
from src.parsers import VariantParser
from src.services import VariantSolverService
from src.settings import Config, setup_logging


async def main(variant_id: str) -> None:
    config = Config()
    setup_logging(config.log_file)

    client = YandexClient(config)

    try:
        fetcher = TaskFetcher(client, config)
        parser = VariantParser()

        service = VariantSolverService(
            fetcher=fetcher,
            parser=parser,
        )

        variant = await service.solve(variant_id)

        print(f"Вариант: {variant.variant_id}")
        print()

        for task in variant.tasks:
            answers = ", ".join(task.answers)

            print(
                f"{task.number}. "
                f"{answers or 'Ответ не найден'}"
            )

    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Использование: uv run solve_variant.py <variant_id>"
        )

    asyncio.run(main(sys.argv[1]))
