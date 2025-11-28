# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Simplified pipe operator disambiguation logic (54% code reduction)**
  - Refactored `_is_binary_context()` method from 215 lines to 98 lines
  - Key insight: Parentheses are irrelevant to pipe operator meaning - only position
    within block/method body matters
  - Removed all parentheses-related checks and complexity
  - Simplified to 4 clear rules:
    1. After block parameters (`:param`), first `|` is parameter terminator (PIPE)
    1. If parameter terminator `|` is followed by `|`, it starts temps (PIPE)
    1. After temp start `|`, next `|` closes temps (PIPE)
    1. All other `|` are binary operators (BINARY_SELECTOR)
  - Added helper method `_is_expression_receiver()` to check if token can receive
    messages
  - All 141 internal tests pass
  - All 223 Soil project files validate successfully (100%)

### Added

- Comprehensive test cases for pipe operator disambiguation:
  - Block parameters inside parentheses
  - Nested blocks with parameters in parentheses
  - Pattern `[ | temp |` (temporary variable closing)
  - Pattern `[ :param | | temp |` (parameters followed by temporaries)
- Complete BNF definitions for STON (Smalltalk Object Notation) types in grammar
  documentation:
  - `<object>`, `<list>`, `<association>`, `<map>`, `<reference>` definitions
  - Referenced from `<mapValue>` in STON metadata specification

### Fixed

- **Pipe operator disambiguation in complex contexts**
  - Fixed tokenization of `|` inside parentheses when blocks are present
  - Pattern `[ :x | (a | b) ]` now correctly tokenizes second `|` as BINARY_SELECTOR
  - Handles real-world code like:
    `self do: [ :pragma | (pragma second | all) ifFalse: [...] ]`
  - Improved from 92.4% (206/223 files) to 100% (223/223 files) validation success on
    Soil project

## [0.1.2] - 2025-01-24

### Added

- Support for array literals with pseudo variables (true, false, nil) in Smalltalk
  parser
- Comprehensive tests for pseudo variables in literal arrays

### Fixed

- Array tokenization to properly handle pseudo variable keywords

## [0.1.1] - 2025-01-23

### Added

- Tests for return statements with assignment and chained assignment expressions
- Enhanced BNF for statement parsing to support optional periods

### Fixed

- Number tokenization improvements
- Return statement parsing with and without trailing periods

## [0.1.0] - 2025-01-20

### Added

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
