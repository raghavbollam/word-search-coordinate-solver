"""Tools that provide a task case and save an agent's submitted decisions."""

from __future__ import annotations

import json
from pathlib import Path

from contract import (
    GitIgnoreDecisionOutput,
    ReadCaseInput,
    ReadCaseOutput,
    WriteDecisionsInput,
    WriteDecisionsOutput,
)
from slimconfig import plain_output


def read_case(given: ReadCaseInput, workspace: Path) -> ReadCaseOutput:
    """Return the task input unchanged."""

    return ReadCaseOutput(
        gitignore_contents=given.task.gitignore_contents,
        candidate_paths=given.task.candidate_paths,
    )


def write_decisions(given: WriteDecisionsInput, workspace: Path) -> WriteDecisionsOutput:
    """Write the agent's final structured answer into its permitted workspace."""

    report = GitIgnoreDecisionOutput(decisions=given.decisions)
    report_path = workspace / "decisions.json"
    report_path.write_text(
        json.dumps(plain_output(report), indent=2) + "\n",
        encoding="utf-8",
    )

    return WriteDecisionsOutput(
        report_path="decisions.json",
        report=report,
    )