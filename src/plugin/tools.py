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
    validate_word_search_input,
)


def read_case(given: ReadCaseInput, workspace: Path) -> ReadCaseOutput:
    """Return the task input unchanged."""

    validate_word_search_input(given.task)

    return ReadCaseOutput(
        grid=given.task.grid,
        target_words=given.task.target_words,
    )


def write_solutions(given: WriteSolutionsInput, workspace: Path) -> WriteSolutionsOutput:
    """Write the agent's final structured answer into its permitted workspace."""

    validate_word_search_input(given.task)
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
