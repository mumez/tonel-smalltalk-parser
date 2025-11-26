# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-01-26

### Fixed

- **Bitwise OR operator in parentheses** (Issue #1 from fix-todo.md)
  - Fixed parser incorrectly interpreting `|` as temporary variable declaration
    delimiter when inside parenthesized expressions
  - The parser now correctly treats `|` as a binary operator (bitwise OR) in expressions
    like `(expr1 | expr2)`
  - Added parentheses depth tracking in lexer's `_is_binary_context()` method
  - Key rule: `|` inside parentheses is always treated as a binary operator, not as a
    temp variable delimiter
  - Affected real-world code:
    - `(pragma arguments second | all)` - now correctly parsed as binary message
    - `((each class == SoilAddKeyEntry) | (each class = SoilRemoveKeyEntry))` - complex
      conditional expressions
  - Added comprehensive test suite with 15 new test cases covering:
    - Simple bitwise OR in parentheses
    - Bitwise OR in conditional expressions (ifTrue:, ifFalse:)
    - Nested parentheses with multiple binary operators
    - Distinction between temp variables and bitwise OR operator
    - Block contexts with both temp variables and bitwise OR

### Added

- `TestBitwiseOrInParentheses` test class with 11 test cases
- `TestLexerBitwiseOrContext` test class with 4 test cases
- Enhanced documentation in `_is_binary_context()` method explaining the key rules

### Technical Details

The fix involved modifying the `SmalltalkLexer._is_binary_context()` method to:

1. Track parentheses depth before checking for block/method context
1. Return `True` (binary operator) when `|` appears inside unclosed parentheses
1. Exclude pipes inside parentheses when counting pipes for temp variable detection
1. Apply the same logic at both block-level and global-level pipe counting

This ensures correct parsing while maintaining backward compatibility with all existing
tests (139 tests pass).

## [0.1.2] - 2025-01-24

### Added (0.1.2)

- Support for array literals with pseudo variables (true, false, nil) in Smalltalk
  parser
- Comprehensive tests for pseudo variables in literal arrays

### Fixed (0.1.2)

- Array tokenization to properly handle pseudo variable keywords

## [0.1.1] - 2025-01-23

### Added (0.1.1)

- Tests for return statements with assignment and chained assignment expressions
- Enhanced BNF for statement parsing to support optional periods

### Fixed (0.1.1)

- Number tokenization improvements
- Return statement parsing with and without trailing periods

## [0.1.0] - 2025-01-20

### Added (0.1.0)

- Initial release of tonel-smalltalk-parser
- Complete Tonel format parser with STON metadata support
- Full Smalltalk method body parser with AST generation
- BNF grammar specification documentation (Japanese)
- CLI tool for Tonel file validation
- Comprehensive test suite
- Support for:
  - Class, Trait, and Extension definitions
  - Method definitions with all selector types (unary, binary, keyword)
  - Temporary variables and block parameters
  - All Smalltalk literals (strings, numbers, symbols, characters, arrays)
  - Message sends (unary, binary, keyword) and cascades
  - Blocks with parameters and temporaries
  - Assignment and return statements
  - Comments and pragmas
  - ANSI Smalltalk features (radix numbers, scaled decimals, thisContext)
