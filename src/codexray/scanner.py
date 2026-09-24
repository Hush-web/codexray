from pathlib import Path


def scan_folder(folder_path: str) -> dict:
    """Walk a folder, count .py files, lines, and bytes."""
    folder = Path(folder_path)
    stats = {
        "files": 0,
        "lines": 0,
        "bytes": 0,
        "files_list": [],
    }

    for file in folder.rglob("*.py"):
     stats["files"] += 1

     try:
        content = file.read_text(encoding="utf-8", errors="ignore")
        lines = len(content.splitlines())     # ← define it first
        size = file.stat().st_size            # ← define it first

        stats["lines"] += lines
        stats["bytes"] += size
        stats["files_list"].append({
            "name": file.name,
            "lines": lines,                   # now this works
            "bytes": size,                    # and this too
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