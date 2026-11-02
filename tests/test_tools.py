import json
from pathlib import Path

from contract import (
    Direction,
    ReadCaseInput,
    WordLocation,
    WordSearchInput,
    WordSearchOutput,
    WriteSolutionsInput,
)
from plugin.tools import read_case, write_solutions

FIXTURES = Path(__file__).parent / "fixtures"


def load_basic_input() -> WordSearchInput:
    data = json.loads((FIXTURES / "basic-case-input.json").read_text(encoding="utf-8"))
    return WordSearchInput(**data)


def load_basic_output() -> WordSearchOutput:
    data = json.loads(
        (FIXTURES / "basic-case-expected.json").read_text(encoding="utf-8")
    )
    return WordSearchOutput(
        solutions=[
            WordLocation(
                word=solution["word"],
                found=solution["found"],
                start_row=solution["start_row"],
                start_column=solution["start_column"],
                end_row=solution["end_row"],
                end_column=solution["end_column"],
                direction=(
                    Direction(solution["direction"])
                    if solution["direction"] is not None
                    else None
                ),
            )
            for solution in data["solutions"]
        ]
    )


def test_read_case_returns_task_input(tmp_path: Path) -> None:
    task = load_basic_input()

    result = read_case(
        ReadCaseInput(task=task),
        tmp_path,
    )

    assert result.grid == task.grid
    assert result.target_words == task.target_words


def test_write_solutions_saves_json_report(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = write_solutions(
        WriteSolutionsInput(
            task=task,
            solutions=expected.solutions,
        ),
        tmp_path,
    )

    assert result.report_path == "solutions.json"
    assert result.report == expected

    saved_report = json.loads((tmp_path / "solutions.json").read_text(encoding="utf-8"))
    assert saved_report == json.loads(
        (FIXTURES / "basic-case-expected.json").read_text(encoding="utf-8")
    )
