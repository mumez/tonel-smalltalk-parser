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
is_valid = full_parser.validate(tonel_content)
print(f"Fully valid: {is_valid}")
```

### Validation

All parsers provide validation methods for checking syntax without parsing:

```python
from tonel_smalltalk_parser import TonelParser, SmalltalkParser, TonelFullParser

# Validate Tonel structure only
tonel_parser = TonelParser()
is_valid_tonel = tonel_parser.validate(tonel_content)
print(f"Valid Tonel structure: {is_valid_tonel}")

# Validate from file
is_valid_file = tonel_parser.validate_from_file("example.st")

# Validate Smalltalk method body
smalltalk_parser = SmalltalkParser()
method_body = "| x | x := 42. ^ x + 1"
is_valid_smalltalk = smalltalk_parser.validate(method_body)
print(f"Valid Smalltalk: {is_valid_smalltalk}")

# Validate both Tonel structure AND Smalltalk method bodies
full_parser = TonelFullParser()
is_fully_valid = full_parser.validate(tonel_content)
print(f"Valid Tonel + Smalltalk: {is_fully_valid}")
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
is_valid = parser.validate(tonel_content)  # Returns False if either is invalid

# Parse from file with full validation
result = parser.parse_from_file("complete_example.st")
is_file_valid = parser.validate_from_file("complete_example.st")
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

- `validate(content: str) -> bool`: Validate string content
- `validate_from_file(filepath: str) -> bool`: Validate file content
- `parse(content: str)`: Parse string content
- `parse_from_file(filepath: str)`: Parse file content

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for
details.
