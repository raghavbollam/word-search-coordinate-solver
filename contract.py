"""Each tool's and task's typed input and output (see nanoagent.plugin.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_CASE = "read_case"
    WRITE_DECISIONS = "write_decisions"


class Task(Enum):
    EXPLAIN_DECISIONS = "explain-decisions"


class DecisionStatus(Enum):
    IGNORED = "ignored"
    INCLUDED = "included"


@dataclass
class GitIgnoreDecisionInput(Output):
    gitignore_contents: Annotated[str, "The contents of the .gitignore file."]
    candidate_paths: Annotated[list[str], "One or more normalized repository-relative candidate paths using '/' separators."]


@dataclass
class PathDecision(Output):
    path: Annotated[str, "One candidate path from the input list."]
    status: Annotated[DecisionStatus, "The decision for this path: either 'ignored' or 'included'."]
    winning_rule: Annotated[int | None, "One-based pattern-only rule number that determined the result, or null where no pattern matched."]
    winning_pattern: Annotated[str | None, "The pattern that determined the result, including '!' for a negation pattern, or null where no pattern matched."]


@dataclass
class GitIgnoreDecisionOutput(Output):
    decisions: Annotated[list[PathDecision], "Exactly one decision for each candidate path in the input list, in the same order as the input list."]


@dataclass
class ReadCaseInput(Output):
    task: Annotated[GitIgnoreDecisionInput, "The task input to inspect."]


@dataclass
class ReadCaseOutput(Output):
    gitignore_contents: str
    candidate_paths: list[str]


@dataclass
class WriteDecisionsInput(Output):
    task: Annotated[GitIgnoreDecisionInput, "The task input copied exactly as given."]
    decisions: Annotated[list[PathDecision], "The final decisions for each candidate path, copied exactly as given."]


@dataclass
class WriteDecisionsOutput(Output):
    report_path: Annotated[str, "The path to the report file that was written, relative to the workspace."]
    report: GitIgnoreDecisionOutput


TOOLS = {
    Tool.READ_CASE: (ReadCaseInput, ReadCaseOutput),
    Tool.WRITE_DECISIONS: (WriteDecisionsInput, WriteDecisionsOutput),
}

TASKS = {
    Task.EXPLAIN_DECISIONS: (GitIgnoreDecisionInput, GitIgnoreDecisionOutput),
}