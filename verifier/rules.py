"""Independently solve word-search grids using the documented canonical order."""

from __future__ import annotations

from contract import Direction, WordLocation, WordSearchInput

DIRECTION_STEPS: tuple[tuple[Direction, int, int], ...] = (
    (Direction.NORTH, -1, 0),
    (Direction.NORTHEAST, -1, 1),
    (Direction.EAST, 0, 1),
    (Direction.SOUTHEAST, 1, 1),
    (Direction.SOUTH, 1, 0),
    (Direction.SOUTHWEST, 1, -1),
    (Direction.WEST, 0, -1),
    (Direction.NORTHWEST, -1, -1),
)


def validate_word_search_input(task: WordSearchInput) -> None:
    """Raise ValueError unless a task has a usable rectangular word-search grid."""

    if not task.grid:
        raise ValueError("grid must contain at least one row.")
    if any(not isinstance(row, str) or not row for row in task.grid):
        raise ValueError("every grid row must be a non-empty string.")

    column_count = len(task.grid[0])
    if any(len(row) != column_count for row in task.grid):
        raise ValueError("grid rows must all have the same length.")

    if not task.target_words:
        raise ValueError("target_words must contain at least one word.")
    if any(not isinstance(word, str) or not word for word in task.target_words):
        raise ValueError("every target word must be a non-empty string.")


def matches_word(
    grid: list[str],
    word: str,
    start_row: int,
    start_column: int,
    row_step: int,
    column_step: int,
) -> bool:
    """Return whether a word fits from one zero-based cell in one direction."""

    row_count = len(grid)
    column_count = len(grid[0])
    end_row = start_row + (len(word) - 1) * row_step
    end_column = start_column + (len(word) - 1) * column_step

    if not (0 <= end_row < row_count and 0 <= end_column < column_count):
        return False

    return all(
        grid[start_row + index * row_step][start_column + index * column_step] == letter
        for index, letter in enumerate(word)
    )


def find_word(grid: list[str], word: str) -> WordLocation:
    """Find a word using row-major start cells and the fixed direction order."""

    validate_word_search_input(WordSearchInput(grid=grid, target_words=[word]))
    return _find_word(grid, word)


def _find_word(grid: list[str], word: str) -> WordLocation:
    """Find a word whose grid and target word have already been validated."""

    for row_index, row in enumerate(grid):
        for column_index, letter in enumerate(row):
            if letter != word[0]:
                continue

            for direction, row_step, column_step in DIRECTION_STEPS:
                if matches_word(grid, word, row_index, column_index, row_step, column_step):
                    end_row = row_index + (len(word) - 1) * row_step
                    end_column = column_index + (len(word) - 1) * column_step
                    return WordLocation(
                        word=word,
                        found=True,
                        start_row=row_index + 1,
                        start_column=column_index + 1,
                        end_row=end_row + 1,
                        end_column=end_column + 1,
                        direction=direction,
                    )

    return WordLocation(
        word=word,
        found=False,
        start_row=None,
        start_column=None,
        end_row=None,
        end_column=None,
        direction=None,
    )


def solve_word_search(grid: list[str], target_words: list[str]) -> list[WordLocation]:
    """Return the canonical solution for every target word in input order."""

    validate_word_search_input(WordSearchInput(grid=grid, target_words=target_words))
    return [_find_word(grid, word) for word in target_words]
