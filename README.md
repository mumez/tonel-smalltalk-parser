# Tonel and Smalltalk Parser

[![Test](https://github.com/mumez/tonel-smalltalk-parser/actions/workflows/test.yml/badge.svg)](https://github.com/mumez/tonel-smalltalk-parser/actions/workflows/test.yml)

A Python library for parsing Tonel-formatted Smalltalk source code with comprehensive
BNF grammar definitions.

## Features

- **Tonel Format Parser**: Handles file structure, metadata (STON format), and method
  references
- **Smalltalk Method Body Parser**: Complete recursive descent parser for Smalltalk
  syntax
- **Full Validation Parser**: Combined parser that validates both Tonel structure and
  Smalltalk method body syntax
- **Validation Methods**: Built-in validation for all parsers with file and string
  support
- **Precise Bracket Matching**: Correctly handles nested blocks and string literals
- **Type Annotations**: Full type support for static analysis
- **Comprehensive Testing**: Extensive test suite covering real-world scenarios

## Grammar Specification

The complete BNF grammar specification is available in:

- [Tonel & Smalltalk BNF Grammar](doc/tonel-and-smalltalk-bnf.md) - Comprehensive
  grammar definition with implementation notes

## Installation

### Install from Git Repository

```bash
# Install directly from GitHub
pip install git+https://github.com/mumez/tonel-smalltalk-parser.git

# Or install with development dependencies
pip install "git+https://github.com/mumez/tonel-smalltalk-parser.git[dev]"
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/mumez/tonel-smalltalk-parser.git
cd tonel-smalltalk-parser

# Install in development mode with uv
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Usage

### Basic Usage Example

```python
from tonel_smalltalk_parser import TonelParser, TonelFullParser

# Basic Tonel parsing (structure only)
parser = TonelParser()
tonel_content = '''
"A sample class for demonstration"
Class {
    #name : #Counter,
    #superclass : #Object,
    #instVars : [ 'value' ],
    #category : #'Demo-Core'
}

{ #category : #accessing }
Counter >> value [
    ^ value
]

{ #category : #accessing }
Counter >> value: anInteger [
    value := anInteger
]
'''

# Parse and access components
result = parser.parse(tonel_content)
print(f"Class: {result.class_definition.metadata.get('name')}")
print(f"Methods: {len(result.methods)}")

# Full validation (Tonel + Smalltalk syntax)
full_parser = TonelFullParser()
is_valid, error_info = full_parser.validate(tonel_content)
print(f"Fully valid: {is_valid}")
if error_info:
    print(f"Validation error: {error_info['reason']} at line {error_info['line']}")
```

### Validation

All parsers provide validation methods for checking syntax without parsing:

```python
from tonel_smalltalk_parser import TonelParser, SmalltalkParser, TonelFullParser

# Validate Tonel structure only
tonel_parser = TonelParser()
is_valid_tonel, error_info = tonel_parser.validate(tonel_content)
print(f"Valid Tonel structure: {is_valid_tonel}")
if error_info:
    print(f"Error at line {error_info['line']}: {error_info['reason']}")

# Validate from file
is_valid_file, error_info = tonel_parser.validate_from_file("example.st")

# Validate Smalltalk method body
smalltalk_parser = SmalltalkParser()
method_body = "| x | x := 42. ^ x + 1"
is_valid_smalltalk, error_info = smalltalk_parser.validate(method_body)
print(f"Valid Smalltalk: {is_valid_smalltalk}")

# Validate both Tonel structure AND Smalltalk method bodies
full_parser = TonelFullParser()
is_fully_valid, error_info = full_parser.validate(tonel_content)
print(f"Valid Tonel + Smalltalk: {is_fully_valid}")
if error_info:
    print(f"Validation failed: {error_info['reason']}")
    print(f"Problem at line {error_info['line']}: {error_info['error_text']}")
```

### Complete Validation with TonelFullParser

For comprehensive validation that checks both Tonel structure and Smalltalk syntax:

```python
from tonel_smalltalk_parser import TonelFullParser

# TonelFullParser validates both Tonel format and Smalltalk method bodies
parser = TonelFullParser()

# This will validate:
# 1. Tonel file structure and metadata
# 2. Each method's Smalltalk syntax
result = parser.parse(tonel_content)  # Raises SyntaxError if invalid Smalltalk
is_valid, error_info = parser.validate(tonel_content)  # Returns (False, error_info) if either is invalid

# Parse from file with full validation
result = parser.parse_from_file("complete_example.st")
is_file_valid, error_info = parser.validate_from_file("complete_example.st")
```

### Smalltalk Method Body Parsing

```python
from tonel_smalltalk_parser import SmalltalkParser

# Parse Smalltalk method body
parser = SmalltalkParser()
method_body = '''
    | block result |
    block := [ :x | x + 1 ].
    result := block value: 5.
    ^ result
'''

ast = parser.parse(method_body)
print(f"AST type: {type(ast).__name__}")
```

### Working with Complex Examples

```python
# Handle methods with nested blocks and complex syntax
complex_method = '''
Counter >> complexCalculation: numbers [
    | sum average |
    sum := numbers inject: 0 into: [ :acc :each | acc + each ].
    average := sum / numbers size.
    ^ self
        logResult: average;
        updateValue: sum;
        yourself
]
'''

result = parser.parse(f"Class {{ #name : #Counter }}\n\n{complex_method}")
method = result.methods[0]
print(f"Method body contains: {len(method.body.split())} tokens")
```

## Command Line Interface

The package provides a command-line tool for validating Tonel files:

```bash
# Install the package to get the CLI command
pip install tonel-smalltalk-parser

# Validate a Tonel file (checks structure + Smalltalk syntax)
validate-tonel path/to/file.st

# Validate only Tonel structure (skip Smalltalk method body validation)
validate-tonel --without-method-body path/to/file.st

# Show help
validate-tonel --help

# Show version
validate-tonel --version
```

### CLI Examples

```bash
# Validate a complete Tonel file
validate-tonel Counter.st
# Output: ✓ 'Counter.st' is valid

# Quick structure-only validation (faster)
validate-tonel --without-method-body Counter.st
# Output: ✓ 'Counter.st' is valid

# Validate invalid file
validate-tonel InvalidFile.st
# Output: ✗ 'InvalidFile.st' contains validation errors
# Error at line 5: No valid class definition found
# >>> invalid tonel content
# Exit code: 1
```

## Development

### Requirements

- Python 3.10+
- Dependencies managed with [uv](https://docs.astral.sh/uv/)

### Development Commands

```bash
# Install dependencies and pre-commit hooks
uv sync
pre-commit install

# Run tests
python -m pytest tests/

# Lint and format code
ruff check src/ tests/
ruff format src/ tests/

# Format markdown documentation
mdformat README.md CLAUDE.md doc/tonel-and-smalltalk-bnf.md

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Architecture

The parser implements a multi-parser architecture:

1. **BaseParser**: Abstract base class providing common validation and file handling
   methods
1. **TonelParser**: Handles the outer Tonel file structure using regex patterns and
   precise bracket matching
1. **SmalltalkParser**: Processes method bodies with a complete recursive descent parser
1. **TonelFullParser**: Combines both parsers for complete validation of Tonel files
   with Smalltalk method body syntax checking
1. **BracketParser**: Utility class for accurate bracket boundary detection

#### Parser Comparison

| Parser            | Validates              | Use Case                             |
| ----------------- | ---------------------- | ------------------------------------ |
| `TonelParser`     | Tonel structure only   | Fast Tonel file structure validation |
| `SmalltalkParser` | Smalltalk syntax only  | Method body syntax validation        |
| `TonelFullParser` | Both Tonel + Smalltalk | Complete file validation             |

All parsers inherit from `BaseParser` and provide:

- `validate(content: str) -> ValidationResult`: Validate string content, returns tuple
  of (success, error_info)
- `validate_from_file(filepath: str) -> ValidationResult`: Validate file content,
  returns tuple of (success, error_info)
- `parse(content: str)`: Parse string content
- `parse_from_file(filepath: str)`: Parse file content

#### ValidationResult

The `validate` and `validate_from_file` methods return a `ValidationResult` tuple
containing:

- `bool`: `True` if validation succeeds, `False` otherwise
- `Optional[Dict]`: Error information if validation fails, `None` if successful
  - `reason`: Description of the error
  - `line`: Line number where the error occurred
  - `error_text`: Text content around the error location

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for
details.
