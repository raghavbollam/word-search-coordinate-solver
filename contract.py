"""Each tool's and task's typed input and output (see nanoagent.plugin.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_CASE = "read_case"
    WRITE_SOLUTIONS = "write_solutions"


class Task(Enum):
    SOLVE_WORD_SEARCH = "solve-word-search"


class Direction(Enum):
    NORTH = "N"
    NORTHEAST = "NE"
    EAST = "E"
    SOUTHEAST = "SE"
    SOUTH = "S"
    SOUTHWEST = "SW"
    WEST = "W"
    NORTHWEST = "NW"


@dataclass
class WordSearchInput(Output):
    grid: Annotated[
        list[str],
        "A non-empty rectangular grid of exact-match characters, one row per string.",
    ]
    target_words: Annotated[
        list[str],
        "One or more non-empty target words to find, preserving the requested output order.",
    ]


@dataclass
class WordLocation(Output):
    word: Annotated[str, "One target word from the input list."]
    found: Annotated[bool, "Whether the target word occurs in the grid."]
    start_row: Annotated[int | None, "One-based row of the first letter, or null when not found."]
    start_column: Annotated[int | None, "One-based column of the first letter, or null when not found."]
    end_row: Annotated[int | None, "One-based row of the final letter, or null when not found."]
    end_column: Annotated[int | None, "One-based column of the final letter, or null when not found."]
    direction: Annotated[
        Direction | None,
        "Direction from the first letter to the final letter, or null when not found.",
    ]


@dataclass
class WordSearchOutput(Output):
    solutions: Annotated[
        list[WordLocation],
        "Exactly one solution for every target word in input order.",
    ]


@dataclass
class ReadCaseInput(Output):
    task: Annotated[WordSearchInput, "The task input to inspect."]


@dataclass
class ReadCaseOutput(Output):
    grid: list[str]
    target_words: list[str]


@dataclass
class WriteSolutionsInput(Output):
    task: Annotated[WordSearchInput, "The task input copied exactly as given."]
    solutions: Annotated[
        list[WordLocation],
        "The final solutions for every target word, copied exactly as given.",
    ]


@dataclass
class WriteSolutionsOutput(Output):
    report_path: Annotated[str, "The report path written relative to the workspace."]
    report: WordSearchOutput


TOOLS = {
    Tool.READ_CASE: (ReadCaseInput, ReadCaseOutput),
    Tool.WRITE_SOLUTIONS: (WriteSolutionsInput, WriteSolutionsOutput),
}

TASKS = {
    Task.SOLVE_WORD_SEARCH: (WordSearchInput, WordSearchOutput),
}
