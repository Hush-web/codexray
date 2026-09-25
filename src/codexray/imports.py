"""Analyze imports and tests in a Python codebase."""

import ast
from pathlib import Path


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


def _extract_imports(content: str) -> tuple[set[str], set[str]]:
    """Return (relative_imports, absolute_imports)."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set(), set()

    relative = set()
    absolute = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                if node.module:
                    relative.add(node.module.split(".")[0])
            else:
                if node.module:
                    absolute.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                absolute.add(alias.name.split(".")[0])

    return relative, absolute


def analyze_imports(folder_path: str) -> dict:
    """Scan a folder and build an import graph."""
    folder = Path(folder_path)

    internal_modules = set()
    file_paths = []
    for file in folder.rglob("*.py"):
        if _is_excluded(file):
            continue
        file_paths.append(file)
        internal_modules.add(file.stem)

    file_imports = {}
    external_used = {}

    for file in file_paths:
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(file.relative_to(folder))
        relative, absolute = _extract_imports(content)

        internal = set(relative)
        for mod in absolute:
            if mod in internal_modules:
                internal.add(mod)
            else:
                external_used.setdefault(mod, set()).add(rel)

        file_imports[rel] = internal

    centrality = {}
    for src, imports in file_imports.items():
        for target in imports:
            centrality[target] = centrality.get(target, 0) + 1

    return {
        "files": file_imports,
        "centrality": centrality,
        "external": external_used,
    }


def find_unused(folder_path: str) -> list[str]:
    """Return files that nothing imports (dead code candidates)."""
    graph = analyze_imports(folder_path)
    files = graph["files"]
    centrality = graph["centrality"]

    skip_names = {"__init__", "__main__", "conftest", "setup"}
    unused = []

    for path in files.keys():
        stem = Path(path).stem
        if stem in skip_names:
            continue
        if stem.startswith("test_") or stem.endswith("_test"):
            continue
        if centrality.get(stem, 0) == 0:
            unused.append(path)

    return sorted(unused)


def find_tests(folder_path: str) -> dict:
    """Detect test files and framework in a Python project."""
    folder = Path(folder_path)

    test_files = []
    has_tests_dir = False
    framework = None

    for file in folder.rglob("*.py"):
        if _is_excluded(file):
            continue
        stem = file.stem
        rel = str(file.relative_to(folder))

        if stem.startswith("test_") or stem.endswith("_test"):
            test_files.append(rel)
        elif "tests" in file.parts and stem not in ("__init__", "conftest"):
            test_files.append(rel)

        if "tests" in file.parts:
            has_tests_dir = True

        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            if "import pytest" in content or "from pytest" in content:
                framework = "pytest"
            elif "import unittest" in content and not framework:
                framework = "unittest"
        except Exception:
            pass

    pyproject = folder / "pyproject.toml"
    if pyproject.exists():
        try:
            if "[tool.pytest" in pyproject.read_text(encoding="utf-8"):
                framework = "pytest"
        except Exception:
            pass

    run_command = {
        "pytest": "pytest",
        "unittest": "python -m unittest discover",
        None: None,
    }.get(framework)

    return {
        "framework": framework,
        "test_files": sorted(test_files),
        "has_tests_dir": has_tests_dir,
        "run_command": run_command,
    }
