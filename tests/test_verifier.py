import json
from pathlib import Path

from contract import (
    Direction,
    Task,
    WordLocation,
    WordSearchInput,
    WordSearchOutput,
)
from verifier import verify_task as verify_registered_task
from verifier.task import verify_task

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


def test_verifier_accepts_correct_solutions(tmp_path: Path) -> None:
    result = verify_task(
        load_basic_input(),
        load_basic_output(),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is True
    assert result.score == 1.0
    assert result.errors == []


def test_verifier_rejects_incorrect_solution(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()
    incorrect_first_solution = WordLocation(
        word="CAT",
        found=False,
        start_row=None,
        start_column=None,
        end_row=None,
        end_column=None,
        direction=None,
    )

    result = verify_task(
        task,
        WordSearchOutput(
            solutions=[incorrect_first_solution, *expected.solutions[1:]]
        ),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert len(result.errors) == 1
    assert "Solution 1 does not match" in result.errors[0]
    assert "CAT" in result.errors[0]


def test_verifier_rejects_missing_solution(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = verify_task(
        task,
        WordSearchOutput(solutions=expected.solutions[:-1]),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert any("Expected 4 solutions, but received 3" in error for error in result.errors)
    assert any("Missing solution 4 for word 'BEE'" in error for error in result.errors)


def test_verifier_rejects_extra_and_reordered_solutions(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = verify_task(
        task,
        WordSearchOutput(
            solutions=[
                expected.solutions[1],
                expected.solutions[0],
                *expected.solutions[2:],
                expected.solutions[0],
            ]
        ),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert any("Expected 4 solutions, but received 5" in error for error in result.errors)
    assert any("Solution 1 does not match" in error for error in result.errors)
    assert any("Solution 2 does not match" in error for error in result.errors)
    assert any("Unexpected extra solution 5" in error for error in result.errors)


def test_registered_verifier_dispatches_to_task_verifier(tmp_path: Path) -> None:
    result = verify_registered_task(
        Task.SOLVE_WORD_SEARCH.value,
        load_basic_input(),
        load_basic_output(),
        reference=None,
        workspace=tmp_path,
    )

    assert result["valid"] is True
    assert result["score"] == 1.0
