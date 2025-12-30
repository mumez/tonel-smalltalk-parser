#!/usr/bin/env python3
"""Command Line Interface for Tonel Smalltalk Linter.

This module provides CLI commands for linting Tonel files.
"""

import argparse
from pathlib import Path
import sys

from .linter import TonelLinter


def main():
    """Run the Tonel linter CLI."""
    parser = argparse.ArgumentParser(
        description="Lint Tonel files for Smalltalk best practices"
    )
    parser.add_argument("target", help="Tonel file or directory to lint")

    args = parser.parse_args()
    target_path = Path(args.target)

    if not target_path.exists():
        print(f"Error: {target_path} not found", file=sys.stderr)
        sys.exit(1)

    # Collect files to lint
    if target_path.is_file():
        if target_path.suffix != ".st":
            print(f"Error: {target_path} is not a .st file", file=sys.stderr)
            sys.exit(1)
        files = [target_path]
    else:
        files = list(target_path.rglob("*.st"))
        # Exclude package.st files
        files = [f for f in files if f.name != "package.st"]

    if not files:
        print(f"No .st files found in {target_path}")
        sys.exit(0)

    # Lint all files
    linter = TonelLinter()
    files_analyzed = 0

    print(f"Linting Tonel files in {target_path}")
    print()

    for file_path in sorted(files):
        issues = linter.lint_from_file(file_path)
        linter.print_issues(file_path, issues)
        files_analyzed += 1

    # Print summary and exit
    exit_code = linter.print_summary(files_analyzed)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
