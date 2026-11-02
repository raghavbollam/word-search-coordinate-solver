import json
from pathlib import Path

from contract import (
    DecisionStatus,
    GitIgnoreDecisionInput,
    GitIgnoreDecisionOutput,
    PathDecision,
    ReadCaseInput,
    WriteDecisionsInput,
)
from plugin.tools import read_case, write_decisions


FIXTURES = Path(__file__).parent / "fixtures"


def load_basic_input() -> GitIgnoreDecisionInput:
    data = json.loads((FIXTURES / "basic-case-input.json").read_text(encoding="utf-8"))
    return GitIgnoreDecisionInput(**data)


def load_basic_output() -> GitIgnoreDecisionOutput:
    data = json.loads((FIXTURES / "basic-case-expected.json").read_text(encoding="utf-8"))

    return GitIgnoreDecisionOutput(
        decisions=[
            PathDecision(
                path=decision["path"],
                status=DecisionStatus(decision["status"]),
                winning_rule=decision["winning_rule"],
                winning_pattern=decision["winning_pattern"],
            )
            for decision in data["decisions"]
        ]
    )


def test_read_case_returns_task_input(tmp_path: Path) -> None:
    task = load_basic_input()

    result = read_case(
        ReadCaseInput(task=task),
        tmp_path,
    )

    assert result.gitignore_contents == task.gitignore_contents
    assert result.candidate_paths == task.candidate_paths


def test_write_decisions_saves_json_report(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = write_decisions(
        WriteDecisionsInput(
            task=task,
            decisions=expected.decisions,
        ),
        tmp_path,
    )

    assert result.report_path == "decisions.json"
    assert result.report == expected

    saved_report = json.loads((tmp_path / "decisions.json").read_text(encoding="utf-8"))

    assert saved_report == {
        "decisions": [
            {
                "path": "app.log",
                "status": "ignored",
                "winning_rule": 1,
                "winning_pattern": "*.log",
            },
            {
                "path": "important.log",
                "status": "included",
                "winning_rule": 3,
                "winning_pattern": "!important.log",
            },
            {
                "path": "cache/session.json",
                "status": "ignored",
                "winning_rule": 2,
                "winning_pattern": "cache/",
            },
            {
                "path": "cache/nested/data.txt",
                "status": "ignored",
                "winning_rule": 2,
                "winning_pattern": "cache/",
            },
            {
                "path": "build/output.log",
                "status": "ignored",
                "winning_rule": 4,
                "winning_pattern": "build/output.log",
            },
            {
                "path": "build/readme.txt",
                "status": "included",
                "winning_rule": None,
                "winning_pattern": None,
            },
            {
                "path": "notes.txt",
                "status": "included",
                "winning_rule": None,
                "winning_pattern": None,
            },
        ]
    }