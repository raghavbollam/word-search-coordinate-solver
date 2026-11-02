"""Deterministic verifier entry points for the gitignore decision explainer."""

from contract import GitIgnoreDecisionOutput, ReadCaseOutput, Task, Tool

from .task import verify_task as verify_explain_decisions


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
        return result(True, "The task input is valid.")

    verdict = verify_explain_decisions(
        value.task,
        GitIgnoreDecisionOutput(decisions=value.decisions),
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

    del workspace

    if Tool(tool) is Tool.READ_CASE:
        expected = ReadCaseOutput(
            gitignore_contents=input_value.task.gitignore_contents,
            candidate_paths=input_value.task.candidate_paths,
        )
        return result(
            output_value == expected,
            "The case was read correctly."
            if output_value == expected
            else "The case output did not match the task input.",
        )

    expected = GitIgnoreDecisionOutput(decisions=input_value.decisions)
    valid = (
        output_value.report_path == "decisions.json"
        and output_value.report == expected
    )
    return result(
        valid,
        "The decisions were written correctly."
        if valid
        else "The decision report did not match the submitted decisions.",
    )


def verify_task(task, arguments, output, reference, workspace):
    """Verify final task output against the independently evaluated decisions."""

    del reference, workspace
    verdict = verify_explain_decisions(arguments, output, None, None)
    return result(
        verdict.ok,
        verdict.message,
        score=verdict.score,
        errors=verdict.errors,
        task=Task(task).value,
    )