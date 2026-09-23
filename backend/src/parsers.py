
from src.models import (
    ExamTaskInfo,
    TaskItem,
    Variant,
    VariantTask,
)


class ExamStructureParser:
    def parse(self, raw: dict) -> dict[int, ExamTaskInfo]:
        result: dict[int, ExamTaskInfo] = {}

        for item in raw.get("data", []):
            number = int(item["exam_task_number"])

            result[number] = ExamTaskInfo(
                number=number,
                skill=item.get("exam_task_tested_skill", ""),
                category_ids=tuple(
                    c["exam_task_category_id"]
                    for c in item.get("task_categories", [])
                ),
            )

        return result


class TaskParser:
    def parse(self, raw: dict) -> TaskItem:
        markup = raw.get("markup", {})

        return TaskItem(
            task_id=raw.get("task_id", ""),
            exam_number=raw.get("number", 0),
            category=raw.get("category_title", ""),
            source=raw.get("task_source_title", ""),
            difficulty=int(raw.get("difficulty_level") or 0),
            answers=self._extract_answers(
                markup.get("answer_control_layout", [])
            ),
            text=self._extract_text(
                markup.get("layout", [])
            ),
        )

    @staticmethod
    def _extract_text(layout: list[dict]) -> str:
        parts = [
            block["content"]["text"]
            for block in layout
            if (
                block.get("kind") == "text"
                and block.get("content", {}).get("text")
            )
        ]

        return "\n\n".join(parts).strip()

    @staticmethod
    def _extract_answers(layout: list[dict]) -> list[str]:
        answers: list[str] = []

        for block in layout:
            if block.get("kind") != "marker":
                continue

            value = block.get("content", {}).get("correct_answers")

            if value is None:
                continue

            if isinstance(value, list):
                answers.extend(str(v) for v in value)
            else:
                answers.append(str(value))

        return answers


class VariantParser:
    def parse(self, raw: dict, variant_id: str) -> Variant:
        tasks: list[VariantTask] = []

        for number, task in enumerate(raw.get("tasks", []), start=1):
            answers = self._extract_answers(task)

            tasks.append(
                VariantTask(
                    number=number,
                    task_id=task.get("task_id", ""),
                    answers=tuple(answers),
                )
            )

        return Variant(
            variant_id=variant_id,
            title=raw.get("title", ""),
            tasks=tuple(tasks),
        )

    @staticmethod
    def _extract_answers(task: dict) -> list[str]:
        markup = task.get("markup", {})
        layout = markup.get("answer_control_layout", [])

        answers: list[str] = []

        for block in layout:
            if block.get("kind") != "marker":
                continue

            value = block.get("content", {}).get("correct_answers")

            if value is None:
                continue

            if isinstance(value, list):
                answers.extend(str(v) for v in value)
            else:
                answers.append(str(value))

        return answers
