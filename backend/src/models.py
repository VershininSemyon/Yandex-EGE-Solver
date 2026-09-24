
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class YandexExamTaskInfo:
    number: int
    skill: str
    category_ids: tuple[str]


@dataclass(slots=True)
class YandexTaskItem:
    task_id: str
    exam_number: int
    category: str
    source: str
    difficulty: int
    answers: list[str]
    text: str


@dataclass(frozen=True, slots=True)
class YandexVariantTask:
    number: int
    task_id: str
    answers: tuple[str]


@dataclass(frozen=True, slots=True)
class YandexVariant:
    variant_id: str
    title: str
    tasks: tuple[YandexVariantTask]


class KompegeDifficultyLevelEnum(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    GROB = 3


@dataclass
class KompegeTask:
    system_uuid: str
    ege_number: int
    task_id: int
    comment: str
    text: str
    key: str
    difficulty: KompegeDifficultyLevelEnum


@dataclass
class KompegeVariant:
    description: str
    tasks: list[KompegeTask]
