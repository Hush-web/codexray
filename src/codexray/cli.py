import argparse
import sys

from .scanner import scan_folder
from .scanner import format_bytes



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
    args = parser.parse_args()

    stats = scan_folder(args.folder)

    if stats["files"] == 0:
        print(f"No .py files found in {args.folder}")
        sys.exit(0)

    print(f"Files:        {stats['files']}")
    print(f"Total lines:  {stats['lines']:,}")
    print(f"Total bytes:  {format_bytes(stats['bytes'])}")
    print("\nLargest files:")
    top = sorted(stats["files_list"], key=lambda f: f["lines"], reverse=True)[:5]
    for f in top:
     print(f"  {f['name']:<20} ({f['lines']} lines)")


if __name__ == "__main__":
    main()