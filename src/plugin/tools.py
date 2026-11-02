"""Tools that provide a word-search case and save an agent's submitted solutions."""

from __future__ import annotations

import json
from pathlib import Path

from slimconfig import plain_output

from contract import (
    ReadCaseInput,
    ReadCaseOutput,
    WordSearchOutput,
    WriteSolutionsInput,
    WriteSolutionsOutput,
)


def _validate_word_search_input(task: ReadCaseInput | WriteSolutionsInput) -> None:
    """Raise ValueError unless a tool receives a usable word-search task."""

    grid = task.task.grid
    target_words = task.task.target_words

    if not grid:
        raise ValueError("grid must contain at least one row.")
    if any(not isinstance(row, str) or not row for row in grid):
        raise ValueError("every grid row must be a non-empty string.")

    column_count = len(grid[0])
    if any(len(row) != column_count for row in grid):
        raise ValueError("grid rows must all have the same length.")

    if not target_words:
        raise ValueError("target_words must contain at least one word.")
    if any(not isinstance(word, str) or not word for word in target_words):
        raise ValueError("every target word must be a non-empty string.")


def read_case(given: ReadCaseInput, workspace: Path) -> ReadCaseOutput:
    """Return the task input unchanged."""

    _validate_word_search_input(given)

    return ReadCaseOutput(
        grid=given.task.grid,
        target_words=given.task.target_words,
    )


def write_solutions(given: WriteSolutionsInput, workspace: Path) -> WriteSolutionsOutput:
    """Write the agent's final structured answer into its permitted workspace."""

    _validate_word_search_input(given)
    report = WordSearchOutput(solutions=given.solutions)
    report_path = workspace / "solutions.json"
    report_path.write_text(
        json.dumps(plain_output(report), indent=2) + "\n",
        encoding="utf-8",
    )

    return WriteSolutionsOutput(
        report_path="solutions.json",
        report=report,
    )
