
import json
from abc import ABC, abstractmethod
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import TaskORM
from src.models import TaskItem


class TaskFileRepository(ABC):
    @abstractmethod
    def save(self, tasks: list[TaskItem], path: str) -> None:
        raise NotImplementedError


class TaskDatabaseRepository(ABC):
    @abstractmethod
    async def save(self, tasks: list[TaskItem]) -> None:
        raise NotImplementedError


class JsonTaskRepository(TaskFileRepository):
    def save(self, tasks: list[TaskItem], path: str) -> None:
        with open(path, mode="w", encoding="utf-8") as file:
            json.dump([asdict(task) for task in tasks], file, ensure_ascii=False, indent=4)


class SqlalchemyTaskRepository(TaskDatabaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, tasks: list[TaskItem]) -> None:
        async with self._session.begin():
            data = [TaskORM(**asdict(task)) for task in tasks]
            self._session.add_all(data)
