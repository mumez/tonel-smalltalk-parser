# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

This is a Tonel and Smalltalk parser project that provides BNF grammar definitions and
parsing capabilities for Tonel-formatted Smalltalk source code. The parser can handle
both Tonel format structure and optionally parse Smalltalk method bodies for source
validation.

## Repository Structure

This repository contains only documentation and grammar specifications:

- `README.md` - Basic project description
- `tonel-and-smalltalk-bnf.md` - Comprehensive BNF grammar specification in Japanese

## Architecture

The project defines a two-parser architecture:

1. **TonelParser** - Handles file structure, metadata (STON format), and method
   references
1. **SmalltalkParser** - Processes method bodies (content between `[` and `]` brackets)

### Key Components Defined in Grammar

**Tonel File Structure:**

- Optional class comments
- Class/Trait/Extension definitions with STON metadata
- Method definitions with metadata, references, and Smalltalk bodies

**STON (Smalltalk Object Notation):**

- Dictionary format with key-value pairs
- Support for symbols, strings, numbers, booleans, and nested structures

**Smalltalk Method Bodies:**

- Complete Smalltalk grammar including expressions, assignments, cascades
- Block syntax with parameter handling
- Literal arrays, dynamic collections, and primitive calls

### Critical Parsing Challenge

The grammar addresses a key parsing challenge: distinguishing between `]` characters
that close Smalltalk blocks within method bodies versus `]` characters that terminate
the method definition itself. The specification provides three resolution strategies:

1. **Bracket Counting** (recommended) - Track nested brackets while respecting string
   and comment boundaries
1. **Smalltalk Parser Preprocessing** - Use dedicated Smalltalk parser to determine
   natural boundaries
1. **Lexical Analysis** - Token-based approach with proper bracket nesting recognition

## Development Notes

This project uses manual parser implementations (not parser generators) for both Tonel
format and Smalltalk method bodies:

- **TonelParser**: Handles Tonel file structure using regex patterns and precise bracket
  matching
- **SmalltalkParser**: Complete recursive descent parser for Smalltalk method body
  syntax
- **BracketParser**: Utility for precise bracket boundary detection in method bodies
- The parsers support full Smalltalk syntax including complex nested structures and edge
  cases

## Development Commands

### Linting and Formatting

- `ruff check src/ tests/` - Run linting checks
- `ruff check --fix src/ tests/` - Run linting with auto-fixes
- `ruff format src/ tests/` - Format code according to style guidelines

### Testing

- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/ -v` - Run tests with verbose output

### Type Checking

This package includes type annotations and a `py.typed` marker file for static type
checking with tools like mypy or pyright.

### Markdown

- `mdformat README.md CLAUDE.md doc/tonel-and-smalltalk-bnf.md` - Format markdown files
- `pymarkdown scan README.md CLAUDE.md doc/tonel-and-smalltalk-bnf.md` - Lint markdown
  files

## Parser Implementation Considerations

When implementing parsers based on this grammar:

1. Handle string literals (`'...'`) and comments (`"..."`) to avoid false bracket
   matches
1. Support character literals (`$]`) that might contain bracket characters
1. Properly track nested block structures (`[ [ ] ]`)
1. Implement STON parsing for metadata sections
1. Consider Unicode support for identifier and string content

## Coding Standards and Style Guidelines

This project follows strict coding standards enforced by pre-commit hooks. When writing
code, adhere to these guidelines to avoid linting errors:

### Line Length

- **Maximum 88 characters per line** (configured in pyproject.toml)
- Break long lines using parentheses, not backslashes
- For long strings, prefer multi-line string formatting or f-string continuation

**Good:**

```python
error_msg = (
    f"Invalid Smalltalk syntax in method "
    f"{method.class_name}>>{method.selector}: {error}"
)
```

**Bad:**

```python
error_msg = f"Invalid Smalltalk syntax in method {method.class_name}>>{method.selector}: {error}"
```

### Docstring Format

- Use triple quotes (`"""`) for all docstrings
- **Always include a blank line between summary and detailed description**
- Follow Google/Sphinx docstring style

**Good:**

```python
def validate(self, content: str) -> bool:
    """Validate if the content can be parsed.

    Args:
        content: The content as a string

    Returns:
        bool: True if content can be parsed successfully, False otherwise
    """
```

**Bad:**

```python
def validate(self, content: str) -> bool:
    """Validate if the content can be parsed.
    Args: ...  # Missing blank line after summary
    """
```

### Import Organization

- Group imports: standard library, third-party, local imports
- Use absolute imports within the package
- Sort imports alphabetically within groups

**Good:**

```python
import os
import tempfile

import pytest

from .base_parser import BaseParser
from .tonel_parser import TonelParser
```

### File Formatting

- **Always end files with a single newline**
- Remove trailing whitespace from all lines
- Use 4 spaces for indentation (no tabs)

### Exception Handling

- Be specific about exception types
- Use `except (Type1, Type2)` for multiple exception types
- Always use `from e` when re-raising exceptions with context

**Good:**

```python
try:
    self.parse(content)
    return True
except (ValueError, SyntaxError, Exception):
    return False
```

### Type Annotations

- Include type hints for all function parameters and return values
- Use `from typing import` for complex types
- Prefer built-in types over typing equivalents when possible (e.g., `list[str]` over
  `List[str]`)

### Code Quality Tools Used

- **ruff**: Linting and code quality (replaces flake8, isort, etc.)
- **ruff format**: Code formatting (replaces black)
- **mdformat**: Markdown formatting
- **markdownlint**: Markdown linting

### Pre-commit Hook Commands

Always run before committing:

```bash
pre-commit run --all-files
```

Or automatically install hooks:

```bash
pre-commit install
```

### Common Linting Errors to Avoid

1. **E501**: Line too long (>88 chars)
1. **D205**: Missing blank line after docstring summary
1. **F401**: Imported but unused
1. **F841**: Local variable assigned but never used
1. **W292**: No newline at end of file

By following these guidelines, your code will pass all pre-commit checks without
requiring manual fixes.
