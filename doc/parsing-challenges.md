# Parsing Challenges and Solutions

This document describes the critical parsing challenges addressed by the
tonel-smalltalk-parser and the solutions implemented.

## 1. Bracket Boundary Detection

The parser must distinguish between `]` characters that close blocks within method
bodies versus `]` that terminate the method definition itself:

```smalltalk
Counter >> process [
    items do: [ :each |
        result := [ each value ] value.  "inner block close"
        ^ result                         "method continues"
    ]                                    "outer block close"
]                                        "method definition close"
```

### Solution: Bracket Counting with Context Awareness

The `BracketParser` class implements a sophisticated bracket tracking algorithm that:

1. **Tracks nested bracket depth** while parsing character by character
1. **Respects string literals** (`'...'`) - brackets inside strings are ignored
1. **Respects comments** (`"..."`) - brackets inside comments are ignored
1. **Handles character literals** (`$]`) - bracket characters as literals are ignored

### Implementation Details

The parser maintains a state machine that tracks:

- Current parsing context (normal, in string, in comment, in character literal)
- Bracket nesting depth
- String and comment boundaries

This ensures accurate identification of the closing `]` that terminates the method
definition.

## 2. Pipe Operator Disambiguation

The `|` character has multiple meanings in Smalltalk:

- **PIPE**: Parameter terminator and temporary variable delimiter
- **BINARY_SELECTOR**: Binary operator (bitwise OR)

### Examples

```smalltalk
[ :param | expr ]              "| is parameter terminator"
[ | temp | expr ]              "| are temp variable delimiters"
[ :param | | temp | expr ]    "first | terminates params, next pair delimits temps"
[ :x | (a | b) ]               "second | is binary OR operator"
```

### Solution: Position-Based Rules

The `SmalltalkLexer` implements position-based rules that ignore parentheses:

1. After block parameters (`:param`), first `|` is parameter terminator (PIPE)
1. If parameter terminator `|` is followed by `|`, it starts temps (PIPE)
1. After temp start `|`, next `|` closes temps (PIPE)
1. All other `|` are binary operators (BINARY_SELECTOR)

### Key Insight

Parentheses are irrelevant to pipe meaning - only the position within block/method body
matters. This simplifies the disambiguation logic significantly.

### Implementation

The `_is_binary_context()` method in `SmalltalkLexer` tracks:

- Block depth
- Parameter terminator state per block level
- Temporary variable delimiter state per block level

This state-based approach correctly identifies pipe operators in all contexts, including
complex nested blocks with mixed usage.

## Related Documentation

- [BNF Grammar Specification](tonel-and-smalltalk-bnf.md) - Complete grammar definition
- [README](../README.md) - Main documentation
