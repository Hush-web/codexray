"""Command-line interface for codexray."""

import argparse
import sys

from .scanner import scan_folder, format_bytes
from .analyzer import build_prompt, get_ai_summary
from .entrypoints import find_entrypoints
from .imports import analyze_imports


def print_report(stats, folder):
    print(f"Analyzing: {folder}")
    print(f"Files:        {stats['files']}")
    print(f"Total lines:  {stats['lines']:,}")
    print(f"Total bytes:  {format_bytes(stats['bytes'])}")

    print("\nLargest files:")
    top = sorted(stats["files_list"], key=lambda f: f["lines"], reverse=True)[:5]
    for f in top:
        print(f"  {f['name']:<20} ({f['lines']} lines)")


def print_entrypoints(folder):
    entries = find_entrypoints(folder)
    if not entries:
        print(f"No entry points found in {folder}")
        return

    print(f"Entry points in {folder}:\n")
    for e in entries:
        if e["type"] == "console-script":
            print(f"  [script]    {e['name']:<15} -> {e['target']}")
        elif e["type"] == "package-main":
            print(f"  [pkg-main]  {e['file']}")
        elif e["type"] == "main-block":
            print(f"  [__main__]  {e['file']}")
        elif e["type"] == "main-function":
            print(f"  [main()]    {e['file']}")


def print_deps(folder):
    graph = analyze_imports(folder)
    centrality = graph["centrality"]
    external = graph["external"]
    files = graph["files"]

    if not files:
        print(f"No Python files found in {folder}")
        return

    print(f"Internal dependencies in {folder}:\n")
    if centrality:
        print("  Most-imported modules:")
        for mod, count in sorted(centrality.items(), key=lambda x: -x[1]):
            print(f"    {mod:<20} (imported by {count} file{'s' if count != 1 else ''})")
    else:
        print("  (no internal imports between files)")

    print()
    if external:
        print(f"  External packages ({len(external)}):")
        for pkg in sorted(external.keys()):
            users = len(external[pkg])
            print(f"    {pkg:<20} ({users} file{'s' if users != 1 else ''})")
    else:
        print("  (no external packages)")

    print()
    leaves = [src for src, imps in files.items() if not imps]
    if leaves:
        print(f"  Files with no internal imports ({len(leaves)}):")
        for f in sorted(leaves):
            print(f"    {f}")


def main():
    parser = argparse.ArgumentParser(
        prog="codexray",
        description="Understand a Python codebase."
    )
    parser.add_argument("folder", nargs="?", default=".")
    parser.add_argument("--entrypoints", action="store_true")
    parser.add_argument("--deps", action="store_true")
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()

    if args.entrypoints:
        print_entrypoints(args.folder)
        return

    if args.deps:
        print_deps(args.folder)
        return

    stats = scan_folder(args.folder)
    if stats["files"] == 0:
        print(f"No code files found in {args.folder}")
        sys.exit(0)

    print_report(stats, args.folder)

    if args.explain:
        print("\n--- AI Summary ---")
        print("Thinking...\n")
        prompt = build_prompt(args.folder, stats["files_list"])
        summary = get_ai_summary(prompt)
        print(summary)


if __name__ == "__main__":
    main()
