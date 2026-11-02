import json
from pathlib import Path

from contract import (
    DecisionStatus,
    GitIgnoreDecisionInput,
    GitIgnoreDecisionOutput,
    PathDecision,
    Task,
)
from verifier.task import verify_task
from verifier import verify_task as verify_registered_task


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


def test_verifier_accepts_correct_decisions(tmp_path: Path) -> None:
    result = verify_task(
        load_basic_input(),
        load_basic_output(),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is True
    assert result.score == 1.0
    assert result.errors == []


def test_verifier_rejects_incorrect_decision(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    incorrect_first_decision = PathDecision(
        path="app.log",
        status=DecisionStatus.INCLUDED,
        winning_rule=None,
        winning_pattern=None,
    )

    result = verify_task(
        task,
        GitIgnoreDecisionOutput(
            decisions=[incorrect_first_decision, *expected.decisions[1:]]
        ),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert len(result.errors) == 1
    assert "Decision 1 does not match" in result.errors[0]
    assert "app.log" in result.errors[0]


def test_verifier_rejects_missing_decision(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = verify_task(
        task,
        GitIgnoreDecisionOutput(decisions=expected.decisions[:-1]),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert any("Expected 7 decisions, but received 6" in error for error in result.errors)
    assert any("Missing decision 7 for path 'notes.txt'" in error for error in result.errors)


def test_verifier_rejects_extra_and_reordered_decisions(tmp_path: Path) -> None:
    task = load_basic_input()
    expected = load_basic_output()

    result = verify_task(
        task,
        GitIgnoreDecisionOutput(
            decisions=[
                expected.decisions[1],
                expected.decisions[0],
                *expected.decisions[2:],
                expected.decisions[0],
            ]
        ),
        reference=None,
        workspace=tmp_path,
    )

    assert result.ok is False
    assert result.score == 0.0
    assert any("Expected 7 decisions, but received 8" in error for error in result.errors)
    assert any("Decision 1 does not match" in error for error in result.errors)
    assert any("Decision 2 does not match" in error for error in result.errors)
    assert any("Unexpected extra decision 8" in error for error in result.errors)

def test_registered_verifier_dispatches_to_task_verifier(tmp_path: Path) -> None:
    result = verify_registered_task(
        Task.EXPLAIN_DECISIONS.value,
        load_basic_input(),
        load_basic_output(),
        reference=None,
        workspace=tmp_path,
    )

    assert result["valid"] is True
    assert result["score"] == 1.0