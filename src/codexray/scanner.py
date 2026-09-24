from pathlib import Path


# File types we count
EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".md", ".txt",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".html", ".css", ".scss",
}

# Folders to skip (they hold third-party code, not your code)
EXCLUDE_DIRS = {
    ".venv", "venv", "env",
    "__pycache__", ".git", ".github",
    "node_modules", "build", "dist",
    ".egg-info", ".pytest_cache", ".mypy_cache",
}

def _is_excluded(path: Path) -> bool:
    """Return True if any part of the path sits inside an excluded folder."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.endswith(".egg-info"):
            return True
    return False

def scan_folder(folder_path: str) -> dict:
    """Walk a folder, count code files, lines, and bytes."""
    folder = Path(folder_path)
    stats = {
        "files": 0,
        "lines": 0,
        "bytes": 0,
        "files_list": [],
    }

    for file in folder.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix not in EXTENSIONS:
            continue
        if _is_excluded(file):
            continue

        stats["files"] += 1
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = len(content.splitlines())
            size = file.stat().st_size

            stats["lines"] += lines
            stats["bytes"] += size
            stats["files_list"].append({
                "name": file.name,
                "path": str(file.relative_to(folder)),   # ← only here
                "lines": lines,
                "bytes": size,
            })
        except Exception as e:
            print(f"  skipped {file.name}: {e}")

    return stats

def format_bytes(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

