"""Evaluate the documented subset of .gitignore patterns independently."""

from __future__ import annotations

from dataclasses import dataclass
import re

from contract import DecisionStatus, PathDecision


@dataclass(frozen=True)
class IgnoreRule:
    """One supported pattern, numbered among patterns only."""

    number: int
    pattern: str
    is_negation: bool


def parse_rules(gitignore_contents: str) -> list[IgnoreRule]:
    """Parse supported patterns, ignoring blank lines and comments."""

    rules: list[IgnoreRule] = []

    for line in gitignore_contents.splitlines():
        pattern = line.strip()

        if not pattern or pattern.startswith("#"):
            continue

        is_negation = pattern.startswith("!")
        actual_pattern = pattern[1:] if is_negation else pattern

        if not actual_pattern:
            continue

        rules.append(
            IgnoreRule(
                number=len(rules) + 1,
                pattern=pattern,
                is_negation=is_negation,
            )
        )

    return rules


def matches(path: str, rule: IgnoreRule) -> bool:
    """Return whether one normalized candidate path matches one supported rule."""

    pattern = rule.pattern[1:] if rule.is_negation else rule.pattern

    if pattern.endswith("/"):
        directory = pattern[:-1]
        return path == directory or path.startswith(f"{directory}/")

    wildcard_pattern = re.escape(pattern).replace(r"\*", ".*")
    return re.fullmatch(wildcard_pattern, path) is not None


def decide_path(path: str, rules: list[IgnoreRule]) -> PathDecision:
    """Apply ordered rules: the last matching supported rule wins."""

    winning_rule: IgnoreRule | None = None

    for rule in rules:
        if matches(path, rule):
            winning_rule = rule

    if winning_rule is None:
        return PathDecision(
            path=path,
            status=DecisionStatus.INCLUDED,
            winning_rule=None,
            winning_pattern=None,
        )

    return PathDecision(
        path=path,
        status=(
            DecisionStatus.INCLUDED
            if winning_rule.is_negation
            else DecisionStatus.IGNORED
        ),
        winning_rule=winning_rule.number,
        winning_pattern=winning_rule.pattern,
    )


def evaluate_paths(
    gitignore_contents: str,
    candidate_paths: list[str],
) -> list[PathDecision]:
    """Return the deterministic decision for every candidate path in order."""

    rules = parse_rules(gitignore_contents)

    return [
        decide_path(path, rules)
        for path in candidate_paths
    ]