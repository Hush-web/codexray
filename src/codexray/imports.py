"""Analyze imports between modules in a Python codebase."""

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
