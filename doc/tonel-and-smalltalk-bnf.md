# Tonel Format - BNF Grammar Specification

## Overview

Tonel is a file-based code storage format used in Pharo Smalltalk. This BNF grammar
formally defines the syntactic structure of the Tonel format.

## Overall Structure

```bnf
<!-- Top-level structure of a Tonel file -->
<tonelFile> ::= <comment>? <classDefinition> <methodDefinitions>
```

## Comment Section

```bnf
<!-- Optional class comment (placed at the beginning of the file) -->
<comment> ::= '"' <commentContent> '"'

<!-- Comment content (including " escaped with "") -->
<commentContent> ::= <anyCharExceptQuote>*

<!-- Characters other than double quotes, or "" escape sequence -->
<anyCharExceptQuote> ::= <char> - '"' | '""'
```

## Class Definition Section

```bnf
<!-- Definition of a class, trait, extension, or package -->
<classDefinition> ::= <type> <whitespace> <stonMap>

<!-- Definition type -->
<type> ::= "Class" | "Trait" | "Extension" | "Package"
```

## Method Definition Section

```bnf
<!-- Zero or more method definitions -->
<methodDefinitions> ::= <methodDefinition>*

<!-- Method definition: metadata + reference + body -->
<methodDefinition> ::= <methodMetadata>? <methodReference> "[" <methodBody> "]"

<!-- Method metadata (category, etc.) -->
<methodMetadata> ::= <stonMap>

<!-- Method reference: class name >> selector -->
<methodReference> ::= <className> <classIndicator>? " >> " <selector>

<!-- " class" indicator for class methods -->
<classIndicator> ::= " class"

<!-- Class name: identifier starting with uppercase letter -->
<className> ::= <upperLetter> <letterOrDigitOrUnderscore>*

<!-- Method selector: one of three types -->
<selector> ::= <identifier> | <keywordSelector> | <binarySelector>

<!-- Keyword selector: concatenation of one or more keywords -->
<keywordSelector> ::= <keyword>+

<!-- Keyword: identifier followed by colon -->
<keyword> ::= <identifier> ":"

<!-- Identifier: starts with letter, followed by letters, digits, or underscores -->
<identifier> ::= <letter> <letterOrDigitOrUnderscore>*

<!-- Reserved identifiers (cannot be used as variable names) -->
<reservedIdentifier> ::= <pseudoVariable>

<!-- Bindable identifier (can be used as variable names) -->
<bindableIdentifier> ::= <identifier> <!-- but not <reservedIdentifier> -->

<!-- Binary selector: one or more special characters -->
<!-- Note: Multi-character operators like <=, >=, ~= are recognized as single tokens -->
<binarySelector> ::= <binaryChar>+

<!-- Characters usable in binary operators -->
<binaryChar> ::= "\\" | "+" | "*" | "/" | "=" | ">" | "<" | "," | "@" | "%" | "~" | "|" | "&" | "-" | "?"

<!-- Method body: delegated to Smalltalk parser -->
<methodBody> ::= <smalltalkExpression>
```

## STON (Smalltalk Object Notation) Section

```bnf
<!-- STON dictionary: key-value pairs enclosed in braces -->
<stonMap> ::= "{" <whitespace>? <mapEntry>? ( "," <whitespace>? <mapEntry> )* <whitespace>? "}"

<!-- Dictionary entry: key : value -->
<mapEntry> ::= <mapKey> <whitespace>? ":" <whitespace>? <mapValue>

<!-- Dictionary key: symbol, string, or number -->
<mapKey> ::= <symbol> | <string> | <number>

<!-- Dictionary value: primitive or composite object -->
<mapValue> ::= <primitive> | <object> | <list> | <association> | <map> | <reference>

<!-- Symbol: identifier prefixed with # -->
<symbol> ::= <simpleSymbol> | <keywordSymbol> | <binarySymbol> | <genericSymbol>

<!-- Simple symbol: restricted character set -->
<simpleSymbol> ::= "#" <simpleSymbolChar>+

<!-- Keyword symbol: identifier with colons -->
<keywordSymbol> ::= "#" <identifier> ( <identifier>? ":" )*

<!-- Binary symbol: binary characters -->
<binarySymbol> ::= "#" <binaryChar>+

<!-- Generic symbol: string format -->
<genericSymbol> ::= "#" <string>

<!-- Characters usable in simple symbols -->
<simpleSymbolChar> ::= <letter> | <digit> | "-" | "_" | "." | "/"

<!-- String: characters enclosed in single quotes -->
<string> ::= "'" <stringContent>* "'"

<!-- String content: normal characters or escape sequences -->
<stringContent> ::= <anyCharExceptSingleQuote> | <escapeSequence>

<!-- Characters other than single quotes -->
<anyCharExceptSingleQuote> ::= <char> - "'"

<!-- Escape sequences -->
<escapeSequence> ::= "\\" ( "'" | "\\" | "r" | "n" | "t" | "u" <hexDigit> <hexDigit> <hexDigit> <hexDigit> )

<!-- Numbers: integers or floating-point numbers -->
<number> ::= <integer> | <scaledDecimal> | <float>

<!-- Integer: decimal or radix-based -->
<integer> ::= <decimalInteger> | <radixInteger>

<decimalInteger> ::= ( "+" | "-" )? <digit>+

<radixInteger> ::= <digit>+ "r" <radixDigit>+

<radixDigit> ::= <digit> | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

<!-- Scaled decimal number (ANSI Smalltalk feature) -->
<scaledDecimal> ::= ( "+" | "-" )? <digit>+ "." <digit>+ "s" <digit>*

<!-- Floating-point number: includes decimal and exponent parts -->
<float> ::= ( "+" | "-" )? <digit>+ "." <digit>+ ( ( "e" | "E" ) ( "+" | "-" )? <digit>+ )?

<!-- Primitive values -->
<primitive> ::= <number> | <string> | <symbol> | <boolean> | <nil>

<!-- Boolean values -->
<boolean> ::= "true" | "false"

<!-- Nil value -->
<nil> ::= "nil"
```

## Lexical Elements

```bnf
<!-- Whitespace characters: space, tab, newline -->
<whitespace> ::= ( " " | "\t" | "\r" | "\n" )+

<!-- Letters -->
<letter> ::= "a"..."z" | "A"..."Z"

<!-- Uppercase letters -->
<upperLetter> ::= "A"..."Z"

<!-- Digits -->
<digit> ::= "0"..."9"

<!-- Hexadecimal digits -->
<hexDigit> ::= <digit> | "a"..."f" | "A"..."F"

<!-- Letters, digits, or underscores -->
<letterOrDigitOrUnderscore> ::= <letter> | <digit> | "_"

<!-- Any Unicode character -->
<char> ::= <anyUnicodeCharacter>

<!-- Method body: sequence of Smalltalk expressions -->
<methodBody> ::= <smalltalkSequence>
```

## Smalltalk Grammar Definition

```bnf
<!-- Smalltalk grammar definition (BNF-ized from ANTLR's Smalltalk.g4) -->
<smalltalkSequence> ::= <temps>? <whitespace>? <statements>?
                      | <whitespace>? <statements>

<!-- Temporary variable declarations -->
<temps> ::= "|" ( <whitespace>? <identifier> )+ <whitespace>? "|"

<!-- Statement list -->
<statements> ::= <answer> <whitespace>? "."? <whitespace>?
               | <expressions> <whitespace>? "." <whitespace>? <answer> <whitespace>? "."? <whitespace>?
               | <expressions> "."? <whitespace>?

<!-- Return statement -->
<answer> ::= "^" <whitespace>? <expression>

<!-- Expression list -->
<expressions> ::= <expression> <expressionList>*

<expressionList> ::= "." <whitespace>? <expression>

<!-- Basic expressions -->
<expression> ::= <assignment>
               | <cascade>
               | <keywordSend>
               | <binarySend>
               | <unarySend>
               | <primitive>
               | <pragma>

<!-- Assignment expression -->
<assignment> ::= <variable> <whitespace>? ":=" <whitespace>? <expression>

<variable> ::= <identifier>

<!-- Cascade (sequential message sending) -->
<cascade> ::= ( <keywordSend> | <binarySend> ) ( <whitespace>? ";" <whitespace>? <message> )+

<message> ::= <binaryMessage> | <unaryMessage> | <keywordMessage>

<!-- Message chain (ANSI Smalltalk style) -->
<messageChain> ::= <unaryMessage>* <binaryMessage>* <keywordMessage>?
                 | <binaryMessage>* <keywordMessage>?
                 | <keywordMessage>

<!-- Types of message sending -->
<keywordSend> ::= <binarySend> <keywordMessage>

<binarySend> ::= <unarySend> <binaryMessage>*

<unarySend> ::= <operand> <unaryMessage>*

<!-- Message details -->
<keywordMessage> ::= <whitespace>? ( <keywordPair> <whitespace>? )+

<keywordPair> ::= <keyword> <whitespace>? <binarySend> <whitespace>?

<binaryMessage> ::= <whitespace>? <binarySelector> <whitespace>? <unarySend>

<unaryMessage> ::= <whitespace>? <identifier>

<!-- Operands (basic elements of expressions) -->
<operand> ::= <literal>
            | <reference>
            | <subexpression>

<reference> ::= <variable>

<subexpression> ::= "(" <whitespace>? <expression> <whitespace>? ")"

<!-- Literals -->
<literal> ::= <runtimeLiteral> | <parsetimeLiteral>

<runtimeLiteral> ::= <dynamicArray> | <block>

<parsetimeLiteral> ::= <pseudoVariable> | <number> | <charConstant>
                     | <literalArray> | <byteArray> | <string> | <symbol>

<!-- Blocks -->
<block> ::= "[" <blockParamList>? <whitespace>? <blockBody>? "]"

<blockParamList> ::= ( <whitespace>? <blockParam> )+ <whitespace>? "|"

<blockParam> ::= ":" <identifier>

<blockBody> ::= <temporaries>? <whitespace>? <statements>?

<!-- Dynamic collections -->
<dynamicArray> ::= "{" <whitespace>? <expressions>? <whitespace>? "}"

<!-- Parse-time literals -->
<pseudoVariable> ::= "nil" | "true" | "false" | "self" | "super" | "thisContext"

<charConstant> ::= "$" <char>

<literalArray> ::= "#(" <literalArrayRest>

<literalArrayRest> ::= <whitespace>? ( <literalArrayItem> <whitespace>? )* ")"

<literalArrayItem> ::= <parsetimeLiteral> | <literalArray> | <identifier> | <binarySelector>

<!-- Byte array: array of integers 0-255 -->
<byteArray> ::= "#[" <whitespace>? ( <byteValue> <whitespace>? )* "]"

<byteValue> ::= <digit>+ <!-- 0 to 255 -->

<!-- Primitive calls and pragmas -->
<primitive> ::= "<" <whitespace>? <keyword> <whitespace>? <digit>+ <whitespace>? ">"

<pragma> ::= "<" <pragmaContent> ">"

<pragmaContent> ::= <identifier> ( <whitespace>? <pragmaItem> )*

<pragmaItem> ::= <string> | <identifier> | ":" | <digit>+ | <binarySelector>
```

## Design Considerations

### Parser Separation

- **TonelParser**: Handles file structure, metadata (STON), and method references
- **SmalltalkParser**: Processes method bodies (content between `[` and `]` brackets)

### Implementation Extensions

The parser implementation includes several extensions beyond the basic BNF:

1. **Enhanced Pragma Support**: Supports complex pragmas with strings and multiple
   parameters

   - `<primitive: 'primitiveJavaScriptErrorRegisterUncaughtInstanceContext:' module: 'CpSystemPlugin'>`
   - `<script>`

1. **Multi-character Binary Operators**: Recognizes compound operators as single tokens

   - `<=`, `>=`, `~=` are tokenized as single binary selectors

1. **Extended Symbol Syntax**: Supports keyword and binary symbols

   - Keyword symbols: `#openDir:options:do:`
   - Binary symbols: `#+`, `#*`

1. **Block Temporaries**: Blocks can have both parameters and temporary variables

   - `[ :stream | | message | message := 'test' ]`

1. **Context-Aware Pipe Handling**: Distinguishes between pipe uses in different
   contexts

   - Block parameter separator: `[ :x | x + 1 ]`
   - Temporary variable delimiter: `[ | temp | temp := 42 ]`
   - Binary message operator: `a | b`

### ANSI Smalltalk Compatibility

This parser provides full implementation of key ANSI Smalltalk compatibility features:

1. **Extended Number Literals**: ✅ **Fully Implemented**

   - Radix integers: `16rFF` (255), `2r1010` (10), `8r777` (511)
   - Scaled decimals: `3.14s2` (precision 2), `123.456s3`
   - Automatic base conversion and validation

1. **Additional Pseudo-variables**: ✅ **Fully Implemented**

   - `thisContext` for execution context access
   - Proper tokenization and parsing support

1. **Byte Array Literals**: ✅ **Fully Implemented**

   - Syntax: `#[1 2 3 255]`, `#[]` (empty arrays)
   - Value validation: 0-255 range enforcement
   - Dedicated AST node: `ByteArray`

1. **Reserved Identifier Classification**: ✅ **Fully Implemented**

   - Validation prevents use of reserved words as variable names
   - Covers: `nil`, `true`, `false`, `self`, `super`, `thisContext`
   - Applies to assignments and temporary variable declarations
   - Clear error messages for violations

**Implementation Status**: All documented ANSI Smalltalk features are fully implemented
and tested with comprehensive test coverage (11 new tests added).

### Boundary Detection Problem and Solutions

**Problem**: Ambiguity of `]` characters due to Smalltalk blocks within methodBody

```smalltalk
MyClass >> example [
    | block |
    block := [ :x | x + 1 ].  ← This ']' ends the block
    ^ block value: 5
]  ← This ']' ends the methodBody
```

**Solution 1: Bracket Counting (Recommended)**

```pseudo
function findMethodBodyEnd(input, startPos):
    pos = startPos  // Right after '['
    bracketCount = 1
    inString = false
    inComment = false

    while pos < input.length and bracketCount > 0:
        char = input[pos]

        if inComment:
            if char == '"':
                inComment = false
        elif inString:
            if char == '\'':
                if pos + 1 < input.length and input[pos + 1] == '\'':
                    pos++  // Escaped quote
                else:
                    inString = false
        else:
            switch char:
                case '"': inComment = true
                case '\'': inString = true
                case '[': bracketCount++
                case ']': bracketCount--

        pos++

    return pos - 1  // Position of the last ']'
```

**Solution 2: Smalltalk Parser Preprocessing**

```pseudo
function parseMethodDefinition(input, startPos):
    // Parse method reference part
    methodRef = parseMethodReference(input, startPos)

    // Expect '['
    expectToken('[')

    // Parse methodBody with Smalltalk parser
    // Parser naturally determines end position
    methodBody = SmalltalkParser.parseMethodBody(input, currentPos)

    // Expect ']'
    expectToken(']')
```

**Solution 3: Lexical Analysis Based**

```bnf
<!-- More precise lexical analysis rules -->
<methodBody> ::= <smalltalkToken>*

<smalltalkToken> ::= <stringLiteral> | <comment> | <block> | <identifier> | <number> | <operator> | <delimiter>

<block> ::= '[' <smalltalkToken>* ']'

<stringLiteral> ::= "'" <stringChar>* "'"

<comment> ::= '"' <commentChar>* '"'
```

### Implementation Considerations

1. **String literals handling**:

   ```smalltalk
   MyClass >> test [
       ^ 'string with ] bracket'
   ]
   ```

1. **Comments handling**:

   ```smalltalk
   MyClass >> test [
       "comment with ] bracket"
       ^ self
   ]
   ```

1. **Nested blocks**:

   ```smalltalk
   MyClass >> test [
       ^ [ [ 1 + 2 ] value ] value
   ]
   ```

1. **Character literals**:

   ```smalltalk
   MyClass >> test [
       ^ $]  "character ']'"
   ]
   ```

### Recommended Approach

**Bracket counting + lexical analysis combination** is most practical:

1. Skip strings (`'...'`)
1. Skip comments (`"..."`)
1. Recognize character literals (`$x`)
1. Increment bracket count for `[`
1. Decrement bracket count for `]`
1. Position where count reaches 0 is the end of methodBody

This method is also used in existing Tonel parser implementations and has proven track
record.

### Usage Example

```smalltalk
"A sample class for demonstration"
Class {
    #name : #Counter,
    #superclass : #Object,
    #instVars : [ 'value' ],
    #category : #'Demo-Core'
}

{ #category : #initialization }
Counter >> initialize [
    super initialize.
    value := 0
]

{ #category : #accessing }
Counter >> value [
    ^ value
]

{ #category : #accessing }
Counter >> value: anInteger [
    value := anInteger
]

{ #category : #arithmetic }
Counter >> + aNumber [
    ^ self value + aNumber
]

{ #category : #'class side' }
Counter class >> new [
    ^ super new initialize
]
```

This BNF grammar formally defines the syntactic structure of the Tonel format and can be
utilized for parser implementation and tool development.
