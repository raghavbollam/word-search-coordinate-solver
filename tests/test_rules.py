import json
from pathlib import Path

from contract import DecisionStatus
from verifier.rules import evaluate_paths, parse_rules


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_rules_ignores_comments_and_blank_lines() -> None:
    rules = parse_rules(
        "# Generated files\n"
        "\n"
        "*.log\n"
        "cache/\n"
        "!important.log\n"
    )

    assert [
        (rule.number, rule.pattern, rule.is_negation)
        for rule in rules
    ] == [
        (1, "*.log", False),
        (2, "cache/", False),
        (3, "!important.log", True),
    ]


def test_evaluate_paths_uses_last_matching_rule() -> None:
    decisions = evaluate_paths(
        "*.log\n"
        "!important.log\n"
        "build/output.log\n",
        [
            "app.log",
            "important.log",
            "build/output.log",
            "notes.txt",
        ],
    )

    assert [
        (
            decision.path,
            decision.status,
            decision.winning_rule,
            decision.winning_pattern,
        )
        for decision in decisions
    ] == [
        ("app.log", DecisionStatus.IGNORED, 1, "*.log"),
        ("important.log", DecisionStatus.INCLUDED, 2, "!important.log"),
        ("build/output.log", DecisionStatus.IGNORED, 3, "build/output.log"),
        ("notes.txt", DecisionStatus.INCLUDED, None, None),
    ]


def test_wildcards_and_directory_rules_apply_to_nested_paths() -> None:
    decisions = evaluate_paths(
        "*.log\n"
        "cache/\n",
        [
            "logs/app.log",
            "cache/session.json",
            "cache/nested/data.txt",
            "src/main.py",
        ],
    )

    assert [
        (
            decision.path,
            decision.status,
            decision.winning_rule,
            decision.winning_pattern,
        )
        for decision in decisions
    ] == [
        ("logs/app.log", DecisionStatus.IGNORED, 1, "*.log"),
        ("cache/session.json", DecisionStatus.IGNORED, 2, "cache/"),
        ("cache/nested/data.txt", DecisionStatus.IGNORED, 2, "cache/"),
        ("src/main.py", DecisionStatus.INCLUDED, None, None),
    ]


def test_empty_gitignore_includes_with_null_metadata() -> None:
    decisions = evaluate_paths("", ["notes.txt"])

    assert [
        (
            decision.status,
            decision.winning_rule,
            decision.winning_pattern,
        )
        for decision in decisions
    ] == [(DecisionStatus.INCLUDED, None, None)]


def test_lone_negation_is_ignored_and_not_numbered() -> None:
    rules = parse_rules("!\n*.log\n")

    assert [
        (rule.number, rule.pattern, rule.is_negation)
        for rule in rules
    ] == [(1, "*.log", False)]


def test_later_ignore_rule_overrides_prior_negation() -> None:
    decision = evaluate_paths("*.log\n!important.log\nimportant.log\n", ["important.log"])[0]

    assert (
        decision.status,
        decision.winning_rule,
        decision.winning_pattern,
    ) == (DecisionStatus.IGNORED, 3, "important.log")


def test_directory_rule_matches_exact_directory_candidate() -> None:
    decision = evaluate_paths("cache/\n", ["cache"])[0]

    assert (
        decision.status,
        decision.winning_rule,
        decision.winning_pattern,
    ) == (DecisionStatus.IGNORED, 1, "cache/")


def test_basic_fixture_matches_expected_decisions() -> None:
    input_data = json.loads(
        (FIXTURES / "basic-case-input.json").read_text(encoding="utf-8")
    )
    expected_data = json.loads(
        (FIXTURES / "basic-case-expected.json").read_text(encoding="utf-8")
    )

    decisions = evaluate_paths(
        input_data["gitignore_contents"],
        input_data["candidate_paths"],
    )

    actual = [
        {
            "path": decision.path,
            "status": decision.status.value,
            "winning_rule": decision.winning_rule,
            "winning_pattern": decision.winning_pattern,
        }
        for decision in decisions
    ]

    assert actual == expected_data["decisions"]