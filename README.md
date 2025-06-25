# Tonel and Smalltalk Parser

A Python library for parsing Tonel-formatted Smalltalk source code with comprehensive
BNF grammar definitions.

## Features

- **Tonel Format Parser**: Handles file structure, metadata (STON format), and method
  references
- **Smalltalk Method Body Parser**: Complete recursive descent parser for Smalltalk
  syntax
- **Precise Bracket Matching**: Correctly handles nested blocks and string literals
- **Type Annotations**: Full type support for static analysis
- **Comprehensive Testing**: Extensive test suite covering real-world scenarios

## Grammar Specification

The complete BNF grammar specification is available in:

- [English BNF Grammar](doc/tonel-and-smalltalk-bnf.md) - Comprehensive grammar
  definition with implementation notes

## Installation

```bash
# Clone the repository
git clone https://github.com/mumez/tonel-smalltalk-parser.git
cd tonel-smalltalk-parser

# Install dependencies with uv
uv sync
```

## Usage

### Basic Tonel Parsing

```python
from tonel_smalltalk_parser import TonelParser

# Parse a Tonel file
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

result = parser.parse(tonel_content)

# Access parsed components
print(f"Class type: {result.class_definition.type}")
print(f"Comment: {result.comment}")
print(f"Number of methods: {len(result.methods)}")

for method in result.methods:
    print(f"Method: {method.class_name} >> {method.selector}")
    print(f"Class method: {method.is_class_method}")
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

The parser implements a two-stage architecture:

1. **TonelParser**: Handles the outer Tonel file structure using regex patterns and
   precise bracket matching
1. **SmalltalkParser**: Processes method bodies with a complete recursive descent parser
1. **BracketParser**: Utility class for accurate bracket boundary detection

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for
details.
