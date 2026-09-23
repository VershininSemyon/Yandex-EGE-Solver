
import io
import json
import re
from dataclasses import asdict
from urllib.parse import parse_qs, urlparse

import uvicorn
from api.config import settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from src.fetchers import TaskFetcher
from src.http import YandexClient
from src.parsers import ExamStructureParser, TaskParser, VariantParser
from src.services import TaskLoaderService, VariantSolverService
from src.settings import Config

app = FastAPI()

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def extract_variant_id(value: str) -> str | None:
    """Извлекает ID варианта из строки, UUID или полной ссылки."""
    value = value.strip()

    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        return value

    parsed_url = urlparse(value)
    query_params = parse_qs(parsed_url.query)

    for key in ("variant_id", "variantId", "id"):
        values = query_params.get(key)
        if values and values[0].strip():
            return values[0].strip()

    uuid_match = re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}",
        value,
    )

    if uuid_match:
        return uuid_match.group(0)

    path_parts = [part for part in parsed_url.path.split("/") if part]

    if path_parts:
        candidate = path_parts[-1].strip()

        if candidate and candidate not in {"variant", "variants"}:
            return candidate

    return None


@app.get("/variants/{variant_id:path}")
async def get_variant(variant_id: str):
    extracted_id = extract_variant_id(variant_id)

    if not extracted_id:
        raise HTTPException(
            status_code=400, 
            detail="Не удалось определить ID варианта. Отправьте валидный UUID или прямую ссылку."
        )

    config = Config()
    client = YandexClient(config)

    try:
        fetcher = TaskFetcher(client, config)
        parser = VariantParser()
        service = VariantSolverService(fetcher=fetcher, parser=parser)

        variant = await service.solve(extracted_id)

        return {
            "variant_id": variant.variant_id,
            "title": variant.title,
            "tasks": [
                {
                    "number": task.number,
                    "answers": list(task.answers),
                }
                for task in variant.tasks
            ],
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail="Неверный id варианта или ошибка при получении данных")
    finally:
        await client.close()


@app.get("/tasks/{task_id}")
async def get_tasks_file(task_id: int):
    config = Config()
    client = YandexClient(config)

    try:
        service = TaskLoaderService(
            TaskFetcher(client, config),
            ExamStructureParser(),
            TaskParser(),
            config,
        )
        
        try:
            tasks = await service.load_by_number(task_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

        tasks_dict = [asdict(task) for task in tasks]
        json_bytes = json.dumps(tasks_dict, ensure_ascii=False, indent=4).encode("utf-8")

        byte_stream = io.BytesIO(json_bytes)
        filename = config.output_file.format(number=task_id)

        return StreamingResponse(
            byte_stream,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    finally:
        await client.close()


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        reload=settings.UVICORN_RELOAD,
        workers=settings.UVICORN_WORKERS_COUNT
    )
