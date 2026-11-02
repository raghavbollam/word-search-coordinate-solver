"""Semantic validation shared by the tools and deterministic verifier."""

from contract import WordSearchInput


def validate_word_search_input(task: WordSearchInput) -> None:
    """Raise ValueError unless a task has a usable rectangular word-search grid."""

    if not task.grid:
        raise ValueError("grid must contain at least one row.")
    if any(not isinstance(row, str) or not row for row in task.grid):
        raise ValueError("every grid row must be a non-empty string.")

    column_count = len(task.grid[0])
    if any(len(row) != column_count for row in task.grid):
        raise ValueError("grid rows must all have the same length.")

    if not task.target_words:
        raise ValueError("target_words must contain at least one word.")
    if any(not isinstance(word, str) or not word for word in task.target_words):
        raise ValueError("every target word must be a non-empty string.")
