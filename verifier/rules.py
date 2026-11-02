"""Independently solve word-search grids using the documented canonical order."""

from __future__ import annotations

from contract import Direction, WordLocation

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

    return [find_word(grid, word) for word in target_words]
