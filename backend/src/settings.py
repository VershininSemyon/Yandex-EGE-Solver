
import logging
from dataclasses import dataclass

TYPE_GET_EXAM_TASKS = "get_tasks_with_categories_request_item"
TYPE_TASK_LIST = "get_task_list_request"
TYPE_GET_VARIANT = "public_get_variant_request_item"


@dataclass(frozen=True, slots=True)
class Config:
    base_url: str = "https://education.yandex.ru"
    csrf_path: str = "/api/v5/get-csrf-token"
    gpttr_path: str = "/api/v5/gpttr"
    subject_id: str = "ac7328ca-dd3d-4bea-8566-9c3177273a57"

    min_task_number: int = 1
    max_task_number: int = 27

    page_size: int = 15

    max_concurrency: int = 5

    use_linked: bool = False

    output_file: str = "tasks_{number}.json"
    log_file: str = "app.log"
    database_url = "sqlite+aiosqlite:///tasks.db"

    user_agent: str = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
    )
    referer: str = "https://education.yandex.ru/ege/inf/tasks"


def setup_logging(log_file: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
