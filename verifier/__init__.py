"""Deterministic verifier entry points for the word-search coordinate solver."""

import json
from pathlib import Path

from contract import (
    ReadCaseOutput,
    Task,
    Tool,
    WordSearchOutput,
)

from .rules import validate_word_search_input
from .task import verify_task as verify_solve_word_search


def result(valid, message, *, score=None, **details):
    """Return a NanoAgent v0001 verifier result."""

    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def serialize_report(report: WordSearchOutput) -> dict[str, list[dict[str, object]]]:
    """Convert the expected report to the JSON representation written by the tool."""

    return {
        "solutions": [
            {
                "word": solution.word,
                "found": solution.found,
                "start_row": solution.start_row,
                "start_column": solution.start_column,
                "end_row": solution.end_row,
                "end_column": solution.end_column,
                "direction": solution.direction.value if solution.direction else None,
            }
            for solution in report.solutions
        ]
    }


def verify_input(tool, value):
    """Validate tool inputs against the deterministic task evaluation."""

    if Tool(tool) is Tool.READ_CASE:
        try:
            validate_word_search_input(value.task)
        except ValueError as error:
            return result(False, "The task input is invalid.", errors=[str(error)])
        return result(True, "The task input is valid.")

    verdict = verify_solve_word_search(
        value.task,
        WordSearchOutput(solutions=value.solutions),
        None,
        None,
    )
    return result(
        verdict.ok,
        verdict.message,
        score=verdict.score,
        errors=verdict.errors,
    )


def verify_output(tool, input_value, output_value, workspace):
    """Validate that each tool returns the value specified by its contract."""

    if Tool(tool) is Tool.READ_CASE:
        expected = ReadCaseOutput(
            grid=input_value.task.grid,
            target_words=input_value.task.target_words,
        )
        return result(
            output_value == expected,
            "The case was read correctly."
            if output_value == expected
            else "The case output did not match the task input.",
        )

    expected = WordSearchOutput(solutions=input_value.solutions)
    expected_report = serialize_report(expected)
    report_file = Path(workspace) / "solutions.json"

    try:
        written_report = json.loads(report_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return result(False, "The solutions report was not written.", errors=["solutions.json is missing."])
    except json.JSONDecodeError as error:
        return result(
            False,
            "The solutions report is not valid JSON.",
            errors=[f"solutions.json could not be decoded: {error.msg}."],
        )

    valid = (
        output_value.report_path == "solutions.json"
        and output_value.report == expected
        and written_report == expected_report
    )
    return result(
        valid,
        "The solutions were written correctly."
        if valid
        else "The solution report did not match the submitted solutions.",
        errors=[] if valid else ["solutions.json or the returned report differs from the submitted solutions."],
    )


def verify_task(task, arguments, output, reference, workspace):
    """Verify final task output against the independently solved answer."""

    del reference, workspace
    verdict = verify_solve_word_search(arguments, output, None, None)
    return result(
        verdict.ok,
        verdict.message,
        score=verdict.score,
        errors=verdict.errors,
        task=Task(task).value,
    )
