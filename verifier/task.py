"""Verify an agent's submitted word-search solutions deterministically."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contract import WordLocation, WordSearchInput, WordSearchOutput

from .rules import solve_word_search


@dataclass(frozen=True)
class VerificationResult:
    """The deterministic verdict for one submitted task answer."""

    ok: bool
    score: float
    message: str
    errors: list[str]


def describe_solution(solution: WordLocation) -> str:
    """Format one solution so mismatches are easy to understand."""

    direction = solution.direction.value if solution.direction else None
    return (
        f"word={solution.word!r}, found={solution.found!r}, "
        f"start=({solution.start_row!r}, {solution.start_column!r}), "
        f"end=({solution.end_row!r}, {solution.end_column!r}), direction={direction!r}"
    )


def verify_task(
    arguments: WordSearchInput,
    output: WordSearchOutput,
    reference: object | None,
    workspace: Path,
) -> VerificationResult:
    """Compare every submitted solution with the independently solved answer."""

    del reference, workspace

    expected = solve_word_search(arguments.grid, arguments.target_words)
    errors: list[str] = []

    if len(output.solutions) != len(expected):
        errors.append(
            f"Expected {len(expected)} solutions, but received {len(output.solutions)}."
        )

    for index, expected_solution in enumerate(expected):
        if index >= len(output.solutions):
            errors.append(
                f"Missing solution {index + 1} for word {expected_solution.word!r}."
            )
            continue

        actual_solution = output.solutions[index]
        if actual_solution != expected_solution:
            errors.append(
                f"Solution {index + 1} does not match. "
                f"Expected ({describe_solution(expected_solution)}); "
                f"received ({describe_solution(actual_solution)})."
            )

    if len(output.solutions) > len(expected):
        for index in range(len(expected), len(output.solutions)):
            errors.append(
                f"Unexpected extra solution {index + 1}: "
                f"({describe_solution(output.solutions[index])})."
            )

    if errors:
        return VerificationResult(
            ok=False,
            score=0.0,
            message="The submitted solutions did not match the deterministic search.",
            errors=errors,
        )

    return VerificationResult(
        ok=True,
        score=1.0,
        message="Every submitted solution matches the deterministic search.",
        errors=[],
    )
