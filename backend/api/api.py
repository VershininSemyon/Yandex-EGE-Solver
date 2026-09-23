import io
import json
from dataclasses import asdict
from uuid import UUID

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


@app.get("/variants/{variant_id}")
async def get_variant(variant_id: UUID):
    config = Config()
    client = YandexClient(config)

    try:
        fetcher = TaskFetcher(client, config)
        parser = VariantParser()
        service = VariantSolverService(fetcher=fetcher, parser=parser)

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
