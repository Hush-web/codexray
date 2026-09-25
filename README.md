# codexray

Understand a Python codebase in seconds.

`codexray` answers the questions you actually have when you open a project
you've never seen before: What is this? Where does execution start? How do
the parts connect? Is there anything broken?

## Install

    pip install codexray

## Usage

    codexray                    # default: files, lines, largest files
    codexray --entrypoints      # where execution starts
    codexray --deps             # internal import graph + external packages
    codexray --unused           # files nothing imports (dead code candidates)
    codexray --tests            # test files and framework
    codexray --onboard          # guided reading order for newcomers
    codexray --json             # machine-readable output of everything
    codexray --explain          # AI summary (requires GROQ_API_KEY)

## Example

    $ codexray /path/to/flask/src/flask --entrypoints

    Entry points in /path/to/flask/src/flask:

      [__main__]  cli.py
      [main()]    cli.py
      [pkg-main]  __main__.py

## Why

Most developers spend 80% of their time *reading* code, not writing it.
`codexray` makes that reading faster — whether you're joining a new team,
returning to an old project, or reviewing code an AI just generated.

## AI mode (optional)

The `--explain` flag sends the largest files to an LLM and returns a plain-English
summary. Uses Groq by default. Set your key:

    export GROQ_API_KEY="gsk_..."

Optional: override the model with `CODEXRAY_MODEL` (default: `openai/gpt-oss-120b`).

## License

MIT
