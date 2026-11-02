import json
from pathlib import Path

import pytest

from contract import Direction
from verifier.rules import find_word, solve_word_search

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("direction", "row_step", "column_step"),
    [
        (Direction.NORTH, -1, 0),
        (Direction.NORTHEAST, -1, 1),
        (Direction.EAST, 0, 1),
        (Direction.SOUTHEAST, 1, 1),
        (Direction.SOUTH, 1, 0),
        (Direction.SOUTHWEST, 1, -1),
        (Direction.WEST, 0, -1),
        (Direction.NORTHWEST, -1, -1),
    ],
)
def test_find_word_supports_every_direction(
    direction: Direction,
    row_step: int,
    column_step: int,
) -> None:
    cells = [["X"] * 5 for _ in range(5)]
    cells[2][2] = "A"
    cells[2 + row_step][2 + column_step] = "B"
    grid = ["".join(row) for row in cells]

    solution = find_word(grid, "AB")

    assert solution.word == "AB"
    assert solution.found is True
    assert (solution.start_row, solution.start_column) == (3, 3)
    assert (solution.end_row, solution.end_column) == (3 + row_step, 3 + column_step)
    assert solution.direction is direction


def test_find_word_uses_documented_direction_order_for_ties() -> None:
    solution = find_word(["AB", "BX"], "AB")

    assert (solution.start_row, solution.start_column) == (1, 1)
    assert solution.direction is Direction.EAST


def test_find_word_uses_row_major_start_cells_for_ties() -> None:
    solution = find_word(["XXX", "XAB", "ABX"], "AB")

    assert (solution.start_row, solution.start_column) == (2, 2)
    assert (solution.end_row, solution.end_column) == (2, 3)
    assert solution.direction is Direction.EAST


def test_one_letter_word_uses_north_direction() -> None:
    solution = find_word(["XQ"], "Q")

    assert solution.found is True
    assert (solution.start_row, solution.start_column) == (1, 2)
    assert (solution.end_row, solution.end_column) == (1, 2)
    assert solution.direction is Direction.NORTH


def test_find_word_returns_documented_not_found_result() -> None:
    solution = find_word(["ABC", "DEF"], "GHI")

    assert solution.word == "GHI"
    assert solution.found is False
    assert (
        solution.start_row,
        solution.start_column,
        solution.end_row,
        solution.end_column,
        solution.direction,
    ) == (None, None, None, None, None)


@pytest.mark.parametrize(
    ("grid", "target_words", "message"),
    [
        ([], ["A"], "grid must contain at least one row"),
        (["AB", "C"], ["A"], "grid rows must all have the same length"),
        (["AB"], [], "target_words must contain at least one word"),
        (["AB"], [""], "every target word must be a non-empty string"),
    ],
)
def test_solve_word_search_rejects_malformed_input(
    grid: list[str],
    target_words: list[str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        solve_word_search(grid, target_words)


def test_basic_fixture_matches_expected_solutions() -> None:
    input_data = json.loads(
        (FIXTURES / "basic-case-input.json").read_text(encoding="utf-8")
    )
    expected_data = json.loads(
        (FIXTURES / "basic-case-expected.json").read_text(encoding="utf-8")
    )

    solutions = solve_word_search(
        input_data["grid"],
        input_data["target_words"],
    )
    actual = [
        {
            "word": solution.word,
            "found": solution.found,
            "start_row": solution.start_row,
            "start_column": solution.start_column,
            "end_row": solution.end_row,
            "end_column": solution.end_column,
            "direction": solution.direction.value if solution.direction else None,
        }
        for solution in solutions
    ]

    assert actual == expected_data["solutions"]
