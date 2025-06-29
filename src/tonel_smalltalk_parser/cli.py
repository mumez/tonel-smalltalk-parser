#!/usr/bin/env python3
"""Command Line Interface for Tonel Smalltalk Parser.

This module provides CLI commands for validating Tonel files and Smalltalk code.
"""

import argparse
from pathlib import Path
import sys

from .tonel_full_parser import TonelFullParser
from .tonel_parser import TonelParser


def validate_tonel_file(file_path: str, without_method_body: bool = False) -> bool:
    """Validate a Tonel file.

    Args:
        file_path: Path to the Tonel file to validate
        without_method_body: If True, only validate Tonel structure without
            Smalltalk method bodies

    Returns:
        True if validation succeeds, False otherwise

    """
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return False

    if not path.is_file():
        print(f"Error: '{file_path}' is not a file", file=sys.stderr)
        return False

    try:
        if without_method_body:
            parser = TonelParser()
            success, error_info = parser.validate_from_file(str(path))
        else:
            parser = TonelFullParser()
            success, error_info = parser.validate_from_file(str(path))

        if success:
            print(f"✓ '{file_path}' is valid")
        else:
            print(f"✗ '{file_path}' contains validation errors")
            if error_info:
                print(
                    f"Error at line {error_info['line']}: {error_info['reason']}",
                    file=sys.stderr,
                )
                if error_info["error_text"]:
                    print(f">>> {error_info['error_text']}", file=sys.stderr)

        return success

    except Exception as e:
        print(f"Error validating '{file_path}': {e}", file=sys.stderr)
        return False


def main() -> int:
    """Run the main CLI application."""
    parser = argparse.ArgumentParser(
        prog="validate-tonel",
        description="Validate Tonel format files and Smalltalk syntax",
    )

    parser.add_argument("file_path", help="Path to the Tonel file to validate")

    parser.add_argument(
        "--without-method-body",
        action="store_true",
        help="Only validate Tonel structure, skip Smalltalk method body validation",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    success = validate_tonel_file(args.file_path, args.without_method_body)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
