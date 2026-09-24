
from src.models import (
    KompegeDifficultyLevelEnum,
    KompegeTask,
    KompegeVariant,
    YandexExamTaskInfo,
    YandexTaskItem,
    YandexVariant,
    YandexVariantTask,
)


class YandexExamStructureParser:
    def parse(self, raw: dict) -> dict[int, YandexExamTaskInfo]:
        result: dict[int, YandexExamTaskInfo] = {}

        for item in raw.get("data", []):
            number = int(item["exam_task_number"])

            result[number] = YandexExamTaskInfo(
                number=number,
                skill=item.get("exam_task_tested_skill", ""),
                category_ids=tuple(
                    c["exam_task_category_id"]
                    for c in item.get("task_categories", [])
                ),
            )

        return result


class YandexTaskParser:
    def parse(self, raw: dict) -> YandexTaskItem:
        markup = raw.get("markup", {})

        return YandexTaskItem(
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


class YandexVariantParser:
    def parse(self, raw: dict, variant_id: str) -> YandexVariant:
        tasks: list[YandexVariantTask] = []

        for number, task in enumerate(raw.get("tasks", []), start=1):
            answers = self._extract_answers(task)

            tasks.append(
                YandexVariantTask(
                    number=number,
                    task_id=task.get("task_id", ""),
                    answers=tuple(answers),
                )
            )

        return YandexVariant(
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


class KompegeTaskParser:
    def parse(self, raw: dict) -> KompegeTask:
        def text_to_html(text: str) -> str:
            return f"""
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Document</title>
                    </head>
                    <body>
                        {text}
                    </body>
                </html>
            """

        return KompegeTask(
            system_uuid=raw.get('id'),
            ege_number=raw.get('number'),
            task_id=raw.get('taskId'),
            comment=raw.get('comment'),
            text=text_to_html(raw.get('text')),
            key=raw.get('key'),
            difficulty=KompegeDifficultyLevelEnum(raw.get('difficulty')),
        )


class KompegeVariantParser:
    def parse(self, raw: dict) -> KompegeVariant:
        task_parser = KompegeTaskParser()
        description = raw.get("description", "")

        tasks = [
            task_parser.parse(task)
            for task in raw.get("tasks", [])
            if task.get("id") is not None
        ]

        return KompegeVariant(
            description=description,
            tasks=tasks
        )
