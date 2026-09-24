import io
import json
from dataclasses import asdict
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from src.settings import Config

from api.config import settings

app = FastAPI()

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/yandex/variants/{variant_id}")
async def get_yandex_variant(variant_id: UUID):
    config = Config()
    client = YandexClient(config)

    try:
        fetcher = YandexTaskFetcher(client, config)
        parser = YandexVariantParser()
        service = YandexVariantSolverService(fetcher=fetcher, parser=parser)

        variant = await service.solve(str(variant_id))

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
        raise HTTPException(status_code=400, detail="Неверный id варианта")
    finally:
        await client.close()


@app.get("/yandex/tasks/{task_id}")
async def get_yandex_tasks_file(task_id: int):
    config = Config()
    client = YandexClient(config)

    try:
        service = YandexTaskLoaderService(
            YandexTaskFetcher(client, config),
            YandexExamStructureParser(),
            YandexTaskParser(),
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


@app.get("/kompege/variants/{variant_id}")
async def get_kompege_variant(variant_id: str):
    config = Config()
    client = KompegeClient()

    try:
        fetcher = KompegeFetcher(client, config)
        parser = KompegeVariantParser()
        service = KompegeVariantSolverService(fetcher=fetcher, parser=parser)

        variant = await service.solve(str(variant_id))

        return {
            "description": variant.description,
            "tasks": [
                {
                    "number": i,
                    "answers": task.key,
                }
                for i, task in enumerate(variant.tasks, 1)
            ],
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail="Неверный id варианта")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        reload=settings.UVICORN_RELOAD,
        workers=settings.UVICORN_WORKERS_COUNT
    )
