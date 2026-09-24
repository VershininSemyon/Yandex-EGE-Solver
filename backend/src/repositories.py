
import json
from abc import ABC, abstractmethod
from dataclasses import asdict

from src.models import YandexTaskItem


class YandexTaskFileRepository(ABC):
    @abstractmethod
    def save(self, tasks: list[YandexTaskItem], path: str) -> None:
        raise NotImplementedError


class JsonYandexTaskRepository(YandexTaskFileRepository):
    def save(self, tasks: list[YandexTaskItem], path: str) -> None:
        with open(path, mode="w", encoding="utf-8") as file:
            json.dump([asdict(task) for task in tasks], file, ensure_ascii=False, indent=4)
