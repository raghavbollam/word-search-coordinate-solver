# Gitignore Decision Explainer

A `nanoagent.plugin/v0001` plugin that determines whether candidate
repository-relative paths are ignored by supplied repository-root `.gitignore`
contents and identifies the final matching rule.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_case` | Reads the `.gitignore` contents and candidate paths for the task | `src/plugin/tools.py` |
| `write_decisions` | Writes the final structured decisions to `decisions.json` in the workspace | `src/plugin/tools.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `explain-decisions` | Determines whether every candidate path is ignored or included | `agent`, with `read_case` and `write_decisions` |

### Supported .gitignore subset

- Exact file or path patterns, such as `notes.txt` and `build/output.log`
- `*` wildcards, which may match `/` characters in a candidate path
- Directory patterns ending in `/`, such as `cache/`; `cache/` matches both
  the exact candidate `cache` and paths below it
- `!` negation patterns, such as `!important.log`
- Rules are processed from top to bottom; the last matching rule wins
- Blank lines, lines beginning with `#`, and a lone `!` are ignored and do not
  receive rule numbers
- An empty `.gitignore` includes every candidate with null rule metadata

`**` recursive globs, nested `.gitignore` files, escaped `#` and `!`, and
full Git directory traversal behavior are out of scope.

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
agent, and deterministic verifier. The verifier independently evaluates the
documented rule subset and checks every submitted decision, including its
status, rule number, and matching pattern.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
```

To publish, push the plugin to a public GitHub repository and submit its URL
through RUSH Lab.
