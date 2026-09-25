"""Command-line interface for codexray."""

import argparse
import json
import sys
from pathlib import Path

from .scanner import scan_folder, format_bytes
from .analyzer import build_prompt, get_ai_summary
from .entrypoints import find_entrypoints
from .imports import analyze_imports, find_unused, find_tests


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


def print_unused(folder):
    unused = find_unused(folder)
    if not unused:
        print(f"No unused files detected in {folder}")
        return

    print(f"Possibly unused files in {folder}:\n")
    for f in unused:
        print(f"  {f}")
    print("\n  (not imported by any other module — may be dead code or an entry point)")


def print_tests(folder):
    info = find_tests(folder)
    print(f"Tests in {folder}:\n")
    print(f"  Framework:    {info['framework'] or 'none detected'}")
    print(f"  Test files:   {len(info['test_files'])}")
    print(f"  Tests folder: {'yes' if info['has_tests_dir'] else 'no'}")
    print(f"  Run with:     {info['run_command'] or '(no framework detected)'}")

    if info["test_files"]:
        print("\n  Test files found:")
        for f in info["test_files"]:
            print(f"    {f}")


def print_onboarding(folder):
    """Guided reading order for someone new to this codebase."""
    scan = scan_folder(folder)
    entries = find_entrypoints(folder)
    graph = analyze_imports(folder)
    tests = find_tests(folder)

    centrality = graph["centrality"]
    files = graph["files"]
    folder_path = Path(folder)

    print(f"Onboarding guide for {folder}:\n")

    step = 1

    if (folder_path / "README.md").exists():
        print(f"  {step}. Start with the README")
        print(f"       README.md")
        print()
        step += 1

    if (folder_path / "pyproject.toml").exists():
        print(f"  {step}. Understand the shape")
        print(f"       pyproject.toml  — dependencies, entry points, config")
        print()
        step += 1

    if centrality:
        print(f"  {step}. Read the core modules (most imported)")
        top = sorted(centrality.items(), key=lambda x: -x[1])[:5]
        for mod, count in top:
            match = None
            for path in files.keys():
                if Path(path).stem == mod:
                    match = path
                    break
            if match:
                lines = next(
                    (f["lines"] for f in scan["files_list"] if f["name"] == Path(match).name),
                    0,
                )
                print(f"       {match:<35} {lines} lines, imported by {count}")
        print()
        step += 1

    if entries:
        print(f"  {step}. Follow execution from the entry points")
        for e in entries[:4]:
            if e["type"] == "console-script":
                print(f"       [script]    {e['name']}  ->  {e['target']}")
            elif e["type"] == "package-main":
                print(f"       [pkg-main]  {e['file']}")
            elif e["type"] == "main-block":
                print(f"       [__main__]  {e['file']}")
        print()
        step += 1

    if tests["framework"]:
        print(f"  {step}. Verify your understanding")
        print(f"       Run tests:  {tests['run_command']}")
        print(f"       Test files: {len(tests['test_files'])}")
        print()
        step += 1

    print("  Skip for now: __init__.py, conftest.py, generated files")


def main():
    parser = argparse.ArgumentParser(
        prog="codexray",
        description="Understand a Python codebase."
    )
    parser.add_argument("folder", nargs="?", default=".")
    parser.add_argument("--entrypoints", action="store_true")
    parser.add_argument("--deps", action="store_true")
    parser.add_argument("--unused", action="store_true")
    parser.add_argument("--tests", action="store_true")
    parser.add_argument("--onboard", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()

    if args.json:
        output = {
            "folder": args.folder,
            "scan": scan_folder(args.folder),
            "entrypoints": find_entrypoints(args.folder),
            "deps": analyze_imports(args.folder),
            "unused": find_unused(args.folder),
            "tests": find_tests(args.folder),
        }
        print(json.dumps(output, indent=2, default=str))
        return

    if args.entrypoints:
        print_entrypoints(args.folder)
        return

    if args.deps:
        print_deps(args.folder)
        return

    if args.unused:
        print_unused(args.folder)
        return

    if args.tests:
        print_tests(args.folder)
        return

    if args.onboard:
        print_onboarding(args.folder)
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
