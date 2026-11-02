"""Verify an agent's submitted gitignore decisions deterministically."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contract import GitIgnoreDecisionInput, GitIgnoreDecisionOutput, PathDecision
from .rules import evaluate_paths


@dataclass(frozen=True)
class VerificationResult:
    """The deterministic verdict for one submitted task answer."""

    ok: bool
    score: float
    message: str
    errors: list[str]


def describe_decision(decision: PathDecision) -> str:
    """Format one decision so mismatches are easy to understand."""

    return (
        f"path={decision.path!r}, "
        f"status={decision.status.value!r}, "
        f"winning_rule={decision.winning_rule!r}, "
        f"winning_pattern={decision.winning_pattern!r}"
    )


def verify_task(
    arguments: GitIgnoreDecisionInput,
    output: GitIgnoreDecisionOutput,
    reference: object | None,
    workspace: Path,
) -> VerificationResult:
    """Compare every submitted decision with the independently evaluated answer."""

    del reference, workspace

    expected = evaluate_paths(
        arguments.gitignore_contents,
        arguments.candidate_paths,
    )

    errors: list[str] = []

    if len(output.decisions) != len(expected):
        errors.append(
            f"Expected {len(expected)} decisions, but received {len(output.decisions)}."
        )

    for index, expected_decision in enumerate(expected):
        if index >= len(output.decisions):
            errors.append(
                f"Missing decision {index + 1} for path {expected_decision.path!r}."
            )
            continue

        actual_decision = output.decisions[index]

        if actual_decision != expected_decision:
            errors.append(
                f"Decision {index + 1} does not match. "
                f"Expected ({describe_decision(expected_decision)}); "
                f"received ({describe_decision(actual_decision)})."
            )

    if len(output.decisions) > len(expected):
        for index in range(len(expected), len(output.decisions)):
            errors.append(
                f"Unexpected extra decision {index + 1}: "
                f"({describe_decision(output.decisions[index])})."
            )

    if errors:
        return VerificationResult(
            ok=False,
            score=0.0,
            message="The submitted decisions did not match the deterministic evaluation.",
            errors=errors,
        )

    return VerificationResult(
        ok=True,
        score=1.0,
        message="Every submitted decision matches the deterministic evaluation.",
        errors=[],
    )