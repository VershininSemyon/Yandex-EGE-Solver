
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExamTaskInfo:
    number: int
    skill: str
    category_ids: tuple[str]


@dataclass(slots=True)
class TaskItem:
    task_id: str
    exam_number: int
    category: str
    source: str
    difficulty: int
    answers: list[str]
    text: str


@dataclass(frozen=True, slots=True)
class VariantTask:
    number: int
    task_id: str
    answers: tuple[str]


@dataclass(frozen=True, slots=True)
class Variant:
    variant_id: str
    title: str
    tasks: tuple[VariantTask]
