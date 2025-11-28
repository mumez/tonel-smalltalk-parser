# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Pipe operator (`|`) parsing accuracy**
  - Fixed incorrect parsing of `|` as temporary variable delimiter when it should be
    bitwise OR operator
  - Now correctly handles complex patterns like `[ :x | (a | b) ]` where the second `|`
    is a binary operator
  - Improved validation success from 92.4% to 100% on real-world Smalltalk code (223
    files tested)

### Added

- Complete BNF grammar definitions for STON (Smalltalk Object Notation) metadata types
  - Added missing definitions: `<object>`, `<list>`, `<association>`, `<map>`,
    `<reference>`

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
