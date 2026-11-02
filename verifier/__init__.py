"""Deterministic verifier entry points for the word-search coordinate solver."""

import json

from slimconfig import plain_output

from contract import (
    ReadCaseOutput,
    Task,
    Tool,
    WordSearchOutput,
    validate_word_search_input,
)

from .task import verify_task as verify_solve_word_search


def result(valid, message, *, score=None, **details):
    """Return a NanoAgent v0001 verifier result."""

    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
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
    expected_report = plain_output(expected)
    report_file = workspace / "solutions.json"

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
