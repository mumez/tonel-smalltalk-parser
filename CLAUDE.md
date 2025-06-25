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
