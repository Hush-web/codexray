import argparse
import sys

from .scanner import scan_folder, format_bytes
from .analyzer import build_prompt, get_ai_summary


def print_report(stats, folder):
    print(f"Analyzing: {folder}")
    print(f"Files:        {stats['files']}")
    print(f"Total lines:  {stats['lines']:,}")
    print(f"Total bytes:  {format_bytes(stats['bytes'])}")

    print("\nLargest files:")
    top = sorted(stats["files_list"], key=lambda f: f["lines"], reverse=True)[:5]
    for f in top:
        print(f"  {f['name']:<20} ({f['lines']} lines)")


def main():
    parser = argparse.ArgumentParser(
        prog="codexray",
        description="Analyze a Python codebase and print a summary."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder to analyze (default: current folder)"
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Use AI to explain what the codebase does"
    )
    args = parser.parse_args()

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