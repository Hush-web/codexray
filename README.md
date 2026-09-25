# codexray

Understand a Python codebase in seconds.

`codexray` answers the questions you actually have when you open a project
you've never seen before: What is this? Where does execution start? How do
the parts connect? Is anything broken?

> **Note on names:** the PyPI package is `hush-codexray`, but the command
> you run is `codexray`. This is common — the package name on PyPI is
> sometimes different from the command it provides.

## Install

    pip install hush-codexray

## Usage

    codexray                    # default: files, lines, largest files
    codexray --entrypoints      # where execution starts
    codexray --deps             # internal import graph + external packages
    codexray --unused           # files nothing imports (dead code candidates)
    codexray --tests            # test files and framework
    codexray --onboard          # guided reading order for newcomers
    codexray --json             # machine-readable output of everything
    codexray --explain          # AI summary (requires GROQ_API_KEY)

All commands take an optional folder argument. Default is the current directory.

    codexray /path/to/project --entrypoints

## Example

    $ codexray . --onboard

    Onboarding guide for .:

      1. Start with the README
           README.md

      2. Understand the shape
           pyproject.toml  — dependencies, entry points, config

      3. Read the core modules (most imported)
           src/codexray/scanner.py      73 lines, imported by 1
           src/codexray/analyzer.py     69 lines, imported by 1
           src/codexray/entrypoints.py  74 lines, imported by 1

      4. Follow execution from the entry points
           [script]    codexray  ->  codexray.cli:main
           [__main__]  src/codexray/cli.py

      5. Verify your understanding
           Run tests:  pytest
           Test files: 0

      Skip for now: __init__.py, conftest.py, generated files

## Why

Most developers spend 80% of their time **reading** code, not writing it.
`codexray` makes that reading faster — whether you're joining a new team,
returning to an old project, or reviewing code an AI just generated.

## Features

| Flag | What it does |
|------|--------------|
| (none) | Count files, lines, bytes; show largest files |
| `--entrypoints` | Find where execution starts (main blocks, console scripts, `__main__.py`) |
| `--deps` | Build the internal import graph and list external packages |
| `--unused` | Find files that nothing else imports (dead code candidates) |
| `--tests` | Detect test files and framework (pytest, unittest) |
| `--onboard` | Produce a guided reading order for someone new |
| `--json` | Dump everything as machine-readable JSON |
| `--explain` | AI summary of the codebase (optional, requires an API key) |

## AI mode (optional)

The `--explain` flag sends the largest files to an LLM and returns a
plain-English summary. Uses Groq by default. Set your key:

    export GROQ_API_KEY="gsk_..."

Override the model with `CODEXRAY_MODEL` (default: `openai/gpt-oss-120b`).

Everything else runs **offline and free** — no network, no API key, no cost.

## Requirements

- Python 3.9+
- `openai` (for `--explain` only)

## License

MIT
