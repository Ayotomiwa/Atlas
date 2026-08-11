from __future__ import annotations

from pathlib import Path
import re


QUESTION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
QUESTION_HEADING_RE = re.compile(
    r"^##\s+Open questions / coverage limits\s*$([\s\S]*?)(?=^##\s+|\Z)",
    re.MULTILINE,
)
QUESTION_HEADERS = ["question id", "question", "affected ids", "evidence gap"]
QUESTION_ANCHOR = "open-questions--coverage-limits"


class QuestionParseError(ValueError):
    def __init__(self, path: str | Path, message: str):
        self.path = Path(path).as_posix()
        self.message = message
        super().__init__(f"{self.path}: {message}")


def _split_table_row(line: str) -> list[str]:
    text = line.strip().strip("|")
    return [cell.replace(r"\|", "|").strip() for cell in re.split(r"(?<!\\)\|", text)]


def _is_separator(cells: list[str]) -> bool:
    return len(cells) == 4 and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells
    )


def parse_open_questions(path: str | Path, body: str, record_id: str) -> list[dict]:
    """Parse the common curated-page question table.

    The body is the semantic source. Callers decide whether a parse failure is a
    generation error or a query diagnostic; deterministic lint does not use this
    parser.
    """

    page = Path(path).as_posix()
    heading = QUESTION_HEADING_RE.search(body)
    if not heading:
        return []

    section = heading.group(1)
    lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if not lines:
        meaningful = section.strip()
        if (
            not meaningful
            or "not covered" in meaningful.casefold()
            or "no open questions" in meaningful.casefold()
        ):
            return []
        raise QuestionParseError(path, "open questions must use the common four-column table")

    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if [cell.casefold() for cell in _split_table_row(line)] == QUESTION_HEADERS
        ),
        None,
    )
    if header_index is None:
        raise QuestionParseError(path, "open-question table has an invalid header")
    if header_index + 1 >= len(lines) or not _is_separator(
        _split_table_row(lines[header_index + 1])
    ):
        raise QuestionParseError(path, "open-question table requires a four-column separator row")

    seen: set[str] = set()
    questions: list[dict] = []
    for line in lines[header_index + 2 :]:
        cells = _split_table_row(line)
        if not any(cells):
            continue
        if len(cells) != 4:
            raise QuestionParseError(path, "open-question rows must contain exactly four columns")
        question_id, question, affected, evidence_gap = cells
        question_id = question_id.strip("`")
        if not QUESTION_ID_RE.fullmatch(question_id) or question_id in seen:
            raise QuestionParseError(path, f"invalid or duplicate open question id {question_id!r}")
        if not question or not evidence_gap:
            raise QuestionParseError(
                path,
                f"open question {question_id} requires question and evidence gap",
            )
        seen.add(question_id)
        affected_ids = (
            []
            if affected.strip() in {"", "-", "—"}
            else [item.strip().strip("`") for item in affected.split(",") if item.strip()]
        )
        questions.append(
            {
                "id": f"{record_id}#{question_id}",
                "question_id": question_id,
                "question": question,
                "affected_ids": affected_ids,
                "evidence_gap": evidence_gap,
                "page": page,
                "anchor": QUESTION_ANCHOR,
            }
        )
    return sorted(questions, key=lambda item: item["id"])
