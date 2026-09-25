"""Find entry points in a Python codebase."""

import re
from pathlib import Path


HAS_MAIN_BLOCK = re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']')
DEF_MAIN = re.compile(r'^def\s+main\s*\(', re.MULTILINE)

SKIP_DIRS = {
    ".venv", "venv", "env",
    "__pycache__", ".git", ".github",
    "node_modules", "build", "dist",
}


def _is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
        if part.endswith(".egg-info"):
            return True
    return False


def find_entrypoints(folder_path: str) -> list[dict]:
    """Scan a folder for entry points."""
    folder = Path(folder_path)
    results = []

    for file in folder.rglob("*.py"):
        if _is_excluded(file):
            continue
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(file.relative_to(folder))

        if file.name == "__main__.py":
            results.append({"type": "package-main", "file": rel})

        if HAS_MAIN_BLOCK.search(content):
            results.append({"type": "main-block", "file": rel})

        if DEF_MAIN.search(content):
            results.append({"type": "main-function", "file": rel})

    pyproject = folder / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            in_scripts = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped == "[project.scripts]":
                    in_scripts = True
                    continue
                if stripped.startswith("[") and in_scripts:
                    in_scripts = False
                    continue
                if in_scripts and "=" in stripped:
                    name, target = stripped.split("=", 1)
                    results.append({
                        "type": "console-script",
                        "file": "pyproject.toml",
                        "name": name.strip(),
                        "target": target.strip(),
                    })
        except Exception:
            pass

    return results
