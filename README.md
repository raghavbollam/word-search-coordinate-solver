# Word Search Coordinate Solver

A `nanoagent.plugin/v0001` plugin for the COMP 480/580 verifiable-tasks
milestone. It finds requested words in a supplied character grid and reports
their canonical coordinates and direction, or an explicit not-found result.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_case` | Reads the grid and ordered target words for the task | `src/plugin/tools.py` |
| `write_solutions` | Writes the final structured locations to `solutions.json` in the workspace | `src/plugin/tools.py` |

### Task

| Task | Does | Runner |
|---|---|---|
| `solve-word-search` | Finds every target word and reports its canonical location or not-found result | `agent`, with `read_case` and `write_solutions` |

## Solver rules

The task input contains a non-empty rectangular `grid` of character strings
and ordered, non-empty `target_words`. Matching is exact and case-sensitive.
Each output `solution` contains the target `word`, a `found` flag, and:

- when found: 1-based `start_row`, `start_column`, `end_row`, `end_column`,
  and a direction from the word's first letter to its final letter;
- when absent: null coordinates and a null direction.

The supported directions are `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, and `NW`.
The verifier chooses a single canonical placement for every target: it scans
possible starting cells in row-major order, then checks directions in exactly
that order. This also makes one-letter words deterministic: their direction is
`N`.

The agent must return exactly one solution for every requested target word in
input order. The deterministic verifier independently runs the same documented
search and rejects missing, extra, reordered, or incorrect results.

## Layout

```text
.
├── nanoagent.yaml
├── contract.py
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env
├── src/plugin/
├── tests/
├── ui/
├── product/
└── verifier/
```

`contract.py` declares the typed inputs and outputs used by the MCP server,
agent, and deterministic verifier. `verifier/rules.py` independently searches
the grid, while `verifier/task.py` checks each submitted location and produces
precise diagnostics.

## Develop and run

```bash
uv sync --extra dev
uv run ruff check .
uv run pytest -q
```

To publish, push the plugin to a public GitHub repository and submit its URL
through RUSH Lab.
