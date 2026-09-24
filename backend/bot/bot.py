
import asyncio
import json
import logging
from dataclasses import asdict

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile, Message
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.fetchers import KompegeFetcher, YandexTaskFetcher
from src.http import KompegeClient, YandexClient
from src.parsers import (
    KompegeVariantParser,
    YandexExamStructureParser,
    YandexTaskParser,
    YandexVariantParser,
)
from src.services import (
    KompegeVariantSolverService,
    YandexTaskLoaderService,
    YandexVariantSolverService,
)
from src.settings import Config, setup_logging

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    telegram_bot_token: str


class BotState(StatesGroup):
    waiting_yandex_variant_id = State()
    waiting_kompege_variant_id = State()
    waiting_yandex_task_number = State()


def build_yandex_variant_service(
    config: Config,
    client: YandexClient,
) -> YandexVariantSolverService:
    return YandexVariantSolverService(
        fetcher=YandexTaskFetcher(client, config),
        parser=YandexVariantParser(),
    )


def build_kompege_variant_service(
    config: Config,
) -> KompegeVariantSolverService:
    return KompegeVariantSolverService(
        fetcher=KompegeFetcher(KompegeClient(), config),
        parser=KompegeVariantParser(),
    )


def build_yandex_task_loader_service(
    config: Config,
    client: YandexClient,
) -> YandexTaskLoaderService:
    return YandexTaskLoaderService(
        fetcher=YandexTaskFetcher(client, config),
        structure_parser=YandexExamStructureParser(),
        task_parser=YandexTaskParser(),
        config=config,
    )


def split_message(
    text: str,
    limit: int = MAX_MESSAGE_LENGTH,
) -> list[str]:
    return [
        text[i : i + limit]
        for i in range(0, len(text), limit)
    ] or [""]


def format_yandex_answers(variant) -> str:
    lines = [
        f"<b>{variant.title or 'Яндекс: вариант'}</b>",
        f"ID: <code>{variant.variant_id}</code>",
        "",
    ]

    for task in variant.tasks:
        answers = ", ".join(task.answers) if task.answers else "Ответ не найден"
        lines.append(
            f"<b>№ {task.number}</b>: <code>{answers}</code>"
        )

    return "\n".join(lines)


def format_kompege_answers(variant) -> str:
    lines = [
        f"<b>{variant.description or 'Kompege: вариант'}</b>",
        "",
    ]

    for number, task in enumerate(variant.tasks, 1):
        answer = task.key or "Ответ не найден"
        lines.append(
            f"<b>№ {number}</b>: <code>{answer}</code>"
        )

    return "\n".join(lines)


router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(
        "<b>EGE Solver</b>\n\n"
        "Бот предоставляет доступ к функциям сервиса "
        "без открытия веб-интерфейса.\n\n"
        "<b>Возможности</b>\n"
        "/solve-yandex-variant — получить ответы "
        "Яндекс-варианта по ID.\n"
        "/solve-kompege-variant — получить ответы "
        "Kompege-варианта по ID.\n"
        "/load-yandex-tasks — загрузить банк заданий "
        "Яндекса по номеру задания.\n\n"
        "<b>Работа с ботом</b>\n"
        "Выберите команду из меню или отправьте её сообщением. "
        "После команды бот запросит необходимые данные.\n\n"
        "Для отмены текущего ввода используйте /cancel."
    )


@router.message(Command("solve-yandex-variant"))
async def solve_yandex_command(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(BotState.waiting_yandex_variant_id)

    await message.answer(
        "<b>Решение Яндекс-варианта</b>\n\n"
        "Отправьте ID варианта.\n"
        "Пример: <code>123e4567-e89b-12d3-a456-426614174000</code>"
    )


@router.message(
    BotState.waiting_yandex_variant_id,
    F.text,
)
async def solve_yandex_variant(
    message: Message,
    state: FSMContext,
    yandex_variant_service: YandexVariantSolverService,
) -> None:
    variant_id = message.text.strip()

    if not variant_id:
        await message.answer(
            "ID варианта не может быть пустым. "
            "Отправьте ID ещё раз."
        )
        return

    await message.answer(
        "Получаю вариант и подготавливаю ответы."
    )

    try:
        variant = await yandex_variant_service.solve(variant_id)
        await state.clear()

        for part in split_message(
            format_yandex_answers(variant)
        ):
            await message.answer(part)

    except Exception:
        logger.exception(
            "Ошибка решения Яндекс-варианта %s",
            variant_id,
        )

        await message.answer(
            "Не удалось получить вариант.\n"
            "Проверьте ID и попробуйте ещё раз."
        )


@router.message(Command("solve-kompege-variant"))
async def solve_kompege_command(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(
        BotState.waiting_kompege_variant_id
    )

    await message.answer(
        "<b>Решение Kompege-варианта</b>\n\n"
        "Отправьте ID варианта.\n"
        "Пример: <code>2771</code>"
    )


@router.message(
    BotState.waiting_kompege_variant_id,
    F.text,
)
async def solve_kompege_variant(
    message: Message,
    state: FSMContext,
    kompege_variant_service: KompegeVariantSolverService,
) -> None:
    variant_id = message.text.strip()

    if not variant_id:
        await message.answer(
            "ID варианта не может быть пустым. "
            "Отправьте ID ещё раз."
        )
        return

    await message.answer(
        "Получаю вариант и подготавливаю ответы."
    )

    try:
        variant = await kompege_variant_service.solve(variant_id)
        await state.clear()

        for part in split_message(
            format_kompege_answers(variant)
        ):
            await message.answer(part)

    except Exception:
        logger.exception(
            "Ошибка решения Kompege-варианта %s",
            variant_id,
        )

        await message.answer(
            "Не удалось получить вариант.\n"
            "Проверьте ID и попробуйте ещё раз."
        )


@router.message(Command("load-yandex-tasks"))
async def load_yandex_tasks_command(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(
        BotState.waiting_yandex_task_number
    )

    await message.answer(
        "<b>Загрузка банка заданий</b>\n\n"
        "Отправьте номер задания от 1 до 27.\n"
        "Бот сформирует JSON-файл со всеми найденными заданиями."
    )


@router.message(
    BotState.waiting_yandex_task_number,
    F.text,
)
async def load_yandex_tasks(
    message: Message,
    state: FSMContext,
    yandex_task_loader_service: YandexTaskLoaderService,
) -> None:
    value = message.text.strip()

    try:
        task_number = int(value)
    except ValueError:
        await message.answer(
            "Номер задания должен быть целым числом от 1 до 27."
        )
        return

    if not 1 <= task_number <= 27:
        await message.answer(
            "Номер задания должен быть от 1 до 27."
        )
        return

    await message.answer(
        "Загружаю задания и формирую JSON-файл."
    )

    try:
        tasks = await yandex_task_loader_service.load_by_number(
            task_number
        )

        payload = json.dumps(
            [asdict(task) for task in tasks],
            ensure_ascii=False,
            indent=4,
        ).encode("utf-8")

        document = BufferedInputFile(
            payload,
            filename=f"tasks_{task_number}.json",
        )

        await message.answer_document(
            document=document,
            caption=(
                f"<b>Задания №{task_number}</b>\n"
                f"Загружено: {len(tasks)}"
            ),
        )

        await state.clear()

    except LookupError as exc:
        await message.answer(
            f"Не удалось найти задания: {exc}"
        )

    except Exception:
        logger.exception(
            "Ошибка загрузки заданий №%s",
            task_number,
        )

        await message.answer(
            "Не удалось загрузить банк заданий. "
            "Попробуйте ещё раз позже."
        )


@router.message(Command("cancel"))
async def cancel(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        "Текущая операция отменена."
    )


async def main() -> None:
    settings = Settings()

    config = Config()
    setup_logging(config.log_file)

    yandex_client = YandexClient(config)

    yandex_variant_service = build_yandex_variant_service(
        config,
        yandex_client,
    )

    yandex_task_loader_service = build_yandex_task_loader_service(
        config,
        yandex_client,
    )

    kompege_variant_service = build_kompege_variant_service(
        config,
    )

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dispatcher = Dispatcher(
        storage=MemoryStorage(),
    )

    dispatcher["yandex_variant_service"] = (
        yandex_variant_service
    )
    dispatcher["yandex_task_loader_service"] = (
        yandex_task_loader_service
    )
    dispatcher["kompege_variant_service"] = (
        kompege_variant_service
    )

    dispatcher.include_router(router)

    try:
        await bot.delete_webhook(
            drop_pending_updates=True,
        )

        await bot.set_my_commands(
            [
                (
                    "start",
                    "О боте и доступных возможностях",
                ),
                (
                    "solve-yandex-variant",
                    "Решить вариант Яндекса",
                ),
                (
                    "solve-kompege-variant",
                    "Решить вариант Kompege",
                ),
                (
                    "load-yandex-tasks",
                    "Загрузить банк заданий",
                ),
                (
                    "cancel",
                    "Отменить текущую операцию",
                ),
            ]
        )

        await dispatcher.start_polling(bot)

    finally:
        await yandex_client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
