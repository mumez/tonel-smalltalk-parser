"""Smalltalk method body parser implementation.

Based on the BNF grammar specification in doc/tonel-and-smalltalk-bnf.md.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Optional

from .base_parser import BaseParser


class TokenType(Enum):
    """Token types for Smalltalk lexical analysis."""

    # Literals
    STRING = "STRING"
    SYMBOL = "SYMBOL"
    NUMBER = "NUMBER"
    CHARACTER = "CHARACTER"

    # Keywords
    NIL = "NIL"
    TRUE = "TRUE"
    FALSE = "FALSE"
    SELF = "SELF"
    SUPER = "SUPER"
    THISCONTEXT = "THISCONTEXT"

    # Identifiers and selectors
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"  # identifier:
    BINARY_SELECTOR = "BINARY_SELECTOR"

    # Delimiters
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LPARRAY = "LPARRAY"  # #(
    LBARRAY = "LBARRAY"  # #[

    # Operators
    ASSIGN = "ASSIGN"  # :=
    RETURN = "RETURN"  # ^
    CASCADE = "CASCADE"  # ;
    PERIOD = "PERIOD"  # .
    PIPE = "PIPE"  # |
    COLON = "COLON"  # :

    # Special
    COMMENT = "COMMENT"
    PRAGMA = "PRAGMA"
    WHITESPACE = "WHITESPACE"
    EOF = "EOF"


@dataclass
class Token:
    """Represents a token in Smalltalk source code."""

    type: TokenType
    value: str
    line: int
    column: int


@dataclass
class SmalltalkExpression:
    """Base class for Smalltalk expressions."""

    pass


@dataclass
class TemporaryVariables(SmalltalkExpression):
    """Temporary variable declarations."""

    variables: list[str]


@dataclass
class Assignment(SmalltalkExpression):
    """Assignment expression."""

    variable: str
    value: SmalltalkExpression


@dataclass
class Return(SmalltalkExpression):
    """Return statement."""

    expression: SmalltalkExpression


@dataclass
class Block(SmalltalkExpression):
    """Block expression."""

    parameters: list[str]
    body: Optional["SmalltalkSequence"]


@dataclass
class MessageSend(SmalltalkExpression):
    """Message send expression."""

    receiver: SmalltalkExpression
    selector: str
    arguments: list[SmalltalkExpression]


@dataclass
class Cascade(SmalltalkExpression):
    """Cascade expression (multiple messages to same receiver)."""

    receiver: SmalltalkExpression
    messages: list[tuple[str, list[SmalltalkExpression]]]  # (selector, arguments)


@dataclass
class Literal(SmalltalkExpression):
    """Literal value."""

    value: Any


@dataclass
class Variable(SmalltalkExpression):
    """Variable reference."""

    name: str


@dataclass
class LiteralArray(SmalltalkExpression):
    """Literal array."""

    elements: list[Any]


@dataclass
class DynamicArray(SmalltalkExpression):
    """Dynamic array."""

    expressions: list[SmalltalkExpression]


@dataclass
class ByteArray(SmalltalkExpression):
    """Byte array literal."""

    values: list[int]


@dataclass
class SmalltalkSequence(SmalltalkExpression):
    """Sequence of Smalltalk statements."""

    temporaries: TemporaryVariables | None
    statements: list[SmalltalkExpression]


class SmalltalkLexer:
    """Lexical analyzer for Smalltalk method bodies."""

    def __init__(self):
        # Token patterns (order matters)
        self.token_patterns = [
            (TokenType.COMMENT, r'"([^"]|"")*"'),
            (
                TokenType.PRAGMA,
                r"<[a-zA-Z][^>]*>",
            ),  # Pragma like <script>, <primitive: 'name' module: 'module'>
            (TokenType.STRING, r"'([^']|'')*'"),
            (TokenType.CHARACTER, r"\$\S"),
            (TokenType.LPARRAY, r"#\("),
            (TokenType.LBARRAY, r"#\["),
            (
                TokenType.SYMBOL,
                r"#[a-zA-Z_][a-zA-Z0-9_]*(?:[a-zA-Z0-9_]*:)*|"
                r"#\'([^\']|\'\')*\'|#[\\+*\/=><@%~&\-?,\|]+",
            ),
            (
                TokenType.NUMBER,
                r"-?\d+r[0-9A-Za-z]+|-?\d+\.\d+s\d*|-?\d+(\.\d+)?([eE][+-]?\d+)?",
            ),
            (TokenType.ASSIGN, r":="),
            (TokenType.RETURN, r"\^"),
            (TokenType.CASCADE, r";"),
            (TokenType.PERIOD, r"\."),
            (TokenType.PIPE, r"\|"),  # Keep this before binary selector
            (TokenType.LPAREN, r"\("),
            (TokenType.RPAREN, r"\)"),
            (TokenType.LBRACKET, r"\["),
            (TokenType.RBRACKET, r"\]"),
            (TokenType.LBRACE, r"\{"),
            (TokenType.RBRACE, r"\}"),
            (
                TokenType.KEYWORD,
                r"[a-zA-Z][a-zA-Z0-9_]*:(?!=)",
            ),  # Keyword not followed by =
            (TokenType.IDENTIFIER, r"[a-zA-Z][a-zA-Z0-9_]*"),
            (
                TokenType.BINARY_SELECTOR,
                r"[\\+*\/=><@%~&\-?,\|]+",
            ),  # Any sequence of binary characters per BNF
            (TokenType.COLON, r":"),
            (TokenType.WHITESPACE, r"\s+"),
        ]

        # Compile patterns
        self.compiled_patterns = [
            (
                token_type,
                re.compile(
                    pattern, re.DOTALL if token_type == TokenType.COMMENT else 0
                ),
            )
            for token_type, pattern in self.token_patterns
        ]

        # Keywords
        self.keywords = {
            "nil": TokenType.NIL,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "self": TokenType.SELF,
            "super": TokenType.SUPER,
            "thisContext": TokenType.THISCONTEXT,
        }

    def tokenize(self, text: str) -> list[Token]:
        """Tokenize Smalltalk source code."""
        tokens = []
        pos = 0
        line_num = 1
        line_start = 0

        while pos < len(text):
            # Try to match each pattern
            matched = False
            for token_type, pattern in self.compiled_patterns:
                match = pattern.match(text, pos)
                if match:
                    value = match.group(0)

                    # Calculate line and column for this token
                    token_line = line_num
                    token_col = pos - line_start + 1

                    # Skip whitespace tokens
                    if token_type != TokenType.WHITESPACE:
                        # Check for keywords
                        if (
                            token_type == TokenType.IDENTIFIER
                            and value in self.keywords
                        ):
                            token_type = self.keywords[value]

                        # Check if | should be treated as binary selector
                        if token_type == TokenType.PIPE and self._is_binary_context(
                            tokens, value
                        ):
                            token_type = TokenType.BINARY_SELECTOR

                        # Handle signed numbers: only - (minus) part of a number
                        if token_type == TokenType.BINARY_SELECTOR and value == "-":
                            # Look ahead to see if this could be a signed number
                            remaining_text = text[match.end() :]
                            number_pattern = r"\d+(\.\d+)?([eE][+-]?\d+)?"
                            number_match = re.match(number_pattern, remaining_text)
                            if number_match and self._is_signed_number_context(tokens):
                                # Combine the sign with the number
                                full_number = value + number_match.group(0)
                                token_type = TokenType.NUMBER
                                value = full_number
                                # Update match end position
                                new_pos = match.end() + number_match.end()
                                pos = new_pos
                                tokens.append(
                                    Token(token_type, value, token_line, token_col)
                                )
                                matched = True
                                break

                        tokens.append(Token(token_type, value, token_line, token_col))

                    # Update position and line tracking
                    new_pos = match.end()
                    # Count newlines in the matched text
                    newline_count = value.count("\n")
                    if newline_count > 0:
                        line_num += newline_count
                        # Find the start of the last line
                        last_newline = value.rfind("\n")
                        line_start = pos + last_newline + 1

                    pos = new_pos
                    matched = True
                    break

            if not matched:
                # Handle newlines for line tracking
                if text[pos] == "\n":
                    line_num += 1
                    line_start = pos + 1
                # Skip unknown characters
                pos += 1

        # Calculate final line number for EOF token
        final_line = line_num
        final_col = pos - line_start
        tokens.append(Token(TokenType.EOF, "", final_line, final_col))
        return tokens

    def _is_binary_context(self, tokens: list[Token], value: str) -> bool:
        """Determine if | should be treated as a binary selector based on context.

        Returns True if | should be treated as binary selector, False if it's a pipe.

        Key rules:
        1. Inside parentheses: | is always a binary operator
        2. At block/method start: | is a temporary variable delimiter
        3. After expression: | is a binary operator
        """
        if not tokens:
            return False

        # First, check if we're inside parentheses by tracking unmatched parens
        paren_depth = 0
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]
            if token.type == TokenType.RPAREN:
                paren_depth += 1
            elif token.type == TokenType.LPAREN:
                paren_depth -= 1
                if paren_depth < 0:
                    # We're inside an unclosed parenthesized expression
                    # In this context, | is always a binary operator
                    return True

        # Not in parentheses, check for block/method temporary variable context
        # Look for the current block context by finding the most recent unmatched [
        bracket_count = 0
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]
            if token.type == TokenType.RBRACKET:
                bracket_count += 1
            elif token.type == TokenType.LBRACKET:
                bracket_count -= 1
                if bracket_count < 0:
                    # Found the opening bracket for current block
                    # Analyze the block content from position i+1 to end
                    block_start = i + 1
                    block_tokens = tokens[block_start:]

                    # Parse block structure: [ :param1 :param2 | temp1 temp2 | stmts ]
                    pos = 0
                    param_count = 0
                    pipe_count = 0

                    # Count parameters (: followed by identifier)
                    while pos < len(block_tokens):
                        if (
                            pos < len(block_tokens) - 1
                            and block_tokens[pos].type == TokenType.COLON
                            and block_tokens[pos + 1].type == TokenType.IDENTIFIER
                        ):
                            param_count += 1
                            pos += 2
                        else:
                            break

                    # Count pipes in the block (excluding those inside parentheses)
                    paren_depth_in_block = 0
                    for bt in block_tokens:
                        if bt.type == TokenType.LPAREN:
                            paren_depth_in_block += 1
                        elif bt.type == TokenType.RPAREN:
                            paren_depth_in_block -= 1
                        elif bt.type == TokenType.PIPE and paren_depth_in_block == 0:
                            pipe_count += 1

                    # Decision logic:
                    # - If we have parameters but no pipes yet, next | separates params
                    # - If we have one pipe after parameters, we might be in temporaries
                    # - If odd number of pipes, next | closes temporaries
                    # - If even pipes and last token is receiver, | is binary

                    if param_count > 0 and pipe_count == 0:
                        # Parameters but no separator yet - this | separates params
                        return False

                    if pipe_count % 2 == 1:
                        # Odd number of pipes means we're in temporaries, | closes them
                        return False

                    # Special case: if we have even pipes and the last token
                    # is an identifier that could be a temp variable (not followed by
                    # something that makes it a receiver), treat | as closing temps
                    if (
                        pipe_count > 0
                        and pipe_count % 2 == 0
                        and len(block_tokens) > 0
                        and block_tokens[-1].type == TokenType.IDENTIFIER
                    ):
                        # Look for pattern: | temp1 temp2 | (temporaries context)
                        # vs temp1 | temp2 (binary message context)

                        # If the identifier comes after a pipe, it's likely a temporary
                        temp_after_pipe = False
                        for j in range(len(block_tokens) - 1, -1, -1):
                            if block_tokens[j].type == TokenType.IDENTIFIER:
                                continue
                            elif block_tokens[j].type == TokenType.PIPE:
                                temp_after_pipe = True
                                break
                            else:
                                break

                        if temp_after_pipe:
                            return False  # This | closes temporaries

                    break

        # If not in a block, use general heuristic
        # General case: odd number of pipes (not in parens) means we're in temporaries
        all_pipe_count = 0
        paren_depth_global = 0
        for t in tokens:
            if t.type == TokenType.LPAREN:
                paren_depth_global += 1
            elif t.type == TokenType.RPAREN:
                paren_depth_global -= 1
            elif t.type == TokenType.PIPE and paren_depth_global == 0:
                all_pipe_count += 1

        if all_pipe_count % 2 == 1:
            return False

        # Look at the last token - if it's a potential receiver, | is binary
        last_token = tokens[-1]
        return last_token.type in [
            TokenType.IDENTIFIER,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.SYMBOL,
            TokenType.CHARACTER,
            TokenType.RPAREN,
            TokenType.RBRACKET,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NIL,
            TokenType.SELF,
            TokenType.SUPER,
            TokenType.THISCONTEXT,
        ]

    def _is_signed_number_context(self, tokens: list[Token]) -> bool:
        """Determine if - (minus) should be treated as part of a signed number.

        Returns True if the - appears in a context where it should be
        part of a number literal rather than a binary operator.
        Note: + is never treated as part of a number in Smalltalk.
        """
        if not tokens:
            return True  # Start of input - can be signed number

        last_token = tokens[-1]

        # First check if this could be a binary operator
        # If the last token can serve as a receiver for binary messages,
        # then - is likely a binary operator
        if last_token.type in [
            TokenType.IDENTIFIER,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.SYMBOL,
            TokenType.CHARACTER,
            TokenType.RPAREN,
            TokenType.RBRACKET,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NIL,
            TokenType.SELF,
            TokenType.SUPER,
            TokenType.THISCONTEXT,
        ]:
            return False  # This is likely a binary operator

        # Contexts where - should be treated as signed number:
        # 1. After operators that expect expressions
        # 2. After opening delimiters
        # 3. After assignment
        # 4. After keywords (in keyword messages)
        return last_token.type in [
            TokenType.ASSIGN,  # x := -5
            TokenType.RETURN,  # ^ -5
            TokenType.LPAREN,  # (-5)
            TokenType.LBRACKET,  # [-5]
            TokenType.LBRACE,  # {-5}
            TokenType.LPARRAY,  # #(-5)
            TokenType.LBARRAY,  # #[-5]
            TokenType.BINARY_SELECTOR,  # x + -5 (after binary operator)
            TokenType.KEYWORD,  # size: -5 (after keyword)
            TokenType.CASCADE,  # obj msg; other: -5
            TokenType.PERIOD,  # stmt. -5
            TokenType.COLON,  # [:x | -5] (block parameter)
            TokenType.PIPE,  # | temp | -5
        ]


class SmalltalkParser(BaseParser):
    """Parser for Smalltalk method bodies."""

    def __init__(self):
        self.lexer = SmalltalkLexer()
        self.tokens = []
        self.current = 0

    def parse(self, method_body: str) -> SmalltalkSequence:
        """Parse Smalltalk method body and return AST."""
        self.tokens = self.lexer.tokenize(method_body)
        self.current = 0
        self._skip_comments()  # Skip any initial comments
        return self._parse_sequence()

    def _current_token(self) -> Token:
        """Get current token."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF token

    def _peek(self, offset: int = 1) -> Token:
        """Peek at token ahead."""
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF token

    def _advance(self) -> Token:
        """Move to next token and return current."""
        token = self._current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        self._skip_comments()
        return token

    def _skip_comments(self) -> None:
        """Skip over comment and pragma tokens."""
        while self.current < len(self.tokens) - 1 and self._current_token().type in (
            TokenType.COMMENT,
            TokenType.PRAGMA,
        ):
            self.current += 1

    def _match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self._current_token().type in token_types

    def _consume(self, token_type: TokenType, message: str | None = None) -> Token:
        """Consume expected token or raise error."""
        if self._match(token_type):
            return self._advance()

        current = self._current_token()
        error_msg = message or f"Expected {token_type}, got {current.type}"
        raise SyntaxError(f"Line {current.line}, Column {current.column}: {error_msg}")

    def _parse_sequence(self) -> SmalltalkSequence:
        """Parse Smalltalk sequence: temps? statements?."""
        temporaries = None
        statements = []

        # Parse temporary variables if present
        if self._match(TokenType.PIPE):
            temporaries = self._parse_temporaries()

        # Parse statements
        statements = self._parse_statements()

        return SmalltalkSequence(temporaries, statements)

    def _parse_temporaries(self) -> TemporaryVariables:
        """Parse temporary variable declarations: | var1 var2 ... |."""
        self._consume(TokenType.PIPE)

        variables = []
        while not self._match(TokenType.PIPE, TokenType.EOF):
            if self._match(TokenType.IDENTIFIER) or self._match(
                TokenType.NIL,
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.SELF,
                TokenType.SUPER,
                TokenType.THISCONTEXT,
            ):
                var_name = self._advance().value
                self._validate_bindable_identifier(var_name)
                variables.append(var_name)
            else:
                break

        self._consume(TokenType.PIPE, "Expected closing '|' for temporaries")
        return TemporaryVariables(variables)

    def _parse_statements(self) -> list[SmalltalkExpression]:
        """Parse sequence of statements."""
        statements = []

        while not self._match(TokenType.EOF, TokenType.RBRACKET):
            # Skip comments between statements
            self._skip_comments()

            # Check if we've reached the end after skipping comments
            if self._match(TokenType.EOF, TokenType.RBRACKET):
                break

            # Skip standalone periods after comments (common in Smalltalk)
            if self._match(TokenType.PERIOD):
                self._advance()
                continue

            # Check for return statement
            if self._match(TokenType.RETURN):
                statements.append(self._parse_return())
                # Handle optional period after return statement
                if self._match(TokenType.PERIOD):
                    self._advance()
                break  # Return is last statement

            # Parse expression
            expr = self._parse_expression()
            if expr:
                statements.append(expr)

            # Handle statement separator (period can follow comments)
            if self._match(TokenType.PERIOD):
                self._advance()
            elif not self._match(TokenType.EOF, TokenType.RBRACKET):
                # Allow end without period
                break

        return statements

    def _parse_return(self) -> Return:
        """Parse return statement: ^ expression."""
        self._consume(TokenType.RETURN)
        expression = self._parse_expression()
        if expression is None:
            raise SyntaxError("Expected expression after '^'")
        return Return(expression)

    def _parse_expression(self) -> SmalltalkExpression | None:
        """Parse expression: assignment | cascade | keywordSend.

        Also handles binarySend | unarySend | primary.
        """
        if not self._current_token() or self._match(TokenType.EOF):
            return None

        # Skip comments at expression level (they should not be statements)
        if self._match(TokenType.COMMENT, TokenType.PRAGMA):
            return None

        # Try assignment
        if self._is_assignment():
            return self._parse_assignment()

        # Parse message send expression
        expr = self._parse_cascade()
        return expr

    def _is_assignment(self) -> bool:
        """Check if current position is an assignment."""
        # Check for identifier or reserved word followed by :=
        return (
            self._match(TokenType.IDENTIFIER)
            or self._match(
                TokenType.NIL,
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.SELF,
                TokenType.SUPER,
                TokenType.THISCONTEXT,
            )
        ) and self._peek().type == TokenType.ASSIGN

    def _parse_assignment(self) -> Assignment:
        """Parse assignment: variable := expression."""
        # Get variable name from either identifier or reserved word
        if self._match(TokenType.IDENTIFIER) or self._match(
            TokenType.NIL,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.SELF,
            TokenType.SUPER,
            TokenType.THISCONTEXT,
        ):
            variable = self._advance().value
        else:
            raise SyntaxError("Expected variable name in assignment")

        self._validate_bindable_identifier(variable)
        self._consume(TokenType.ASSIGN)
        value = self._parse_expression()
        if value is None:
            raise SyntaxError("Expected expression after ':='")
        return Assignment(variable, value)

    def _parse_cascade(self) -> SmalltalkExpression:
        """Parse cascade: expression (; message)*."""
        expr = self._parse_keyword_send()

        if self._match(TokenType.CASCADE):
            # Extract the receiver from the first message
            if isinstance(expr, MessageSend):
                receiver = expr.receiver
                # The first message is part of the cascade
                messages = [(expr.selector, expr.arguments)]
            else:
                receiver = expr
                messages = []

            # Parse additional cascade messages
            while self._match(TokenType.CASCADE):
                self._advance()  # consume ;
                # Parse message at the appropriate precedence level
                if self._match(TokenType.KEYWORD):
                    # Keyword message
                    selector_parts = []
                    arguments = []
                    while self._match(TokenType.KEYWORD):
                        keyword = self._advance().value
                        selector_parts.append(keyword)
                        arg = self._parse_binary_send()
                        arguments.append(arg)
                    selector = "".join(selector_parts)
                    messages.append((selector, arguments))
                elif self._match(TokenType.BINARY_SELECTOR):
                    # Binary message
                    selector = self._advance().value
                    arg = self._parse_unary_send()
                    messages.append((selector, [arg]))
                elif self._match(TokenType.IDENTIFIER):
                    # Unary message
                    selector = self._advance().value
                    messages.append((selector, []))
                else:
                    raise SyntaxError("Expected message selector after ';'")

            return Cascade(receiver, messages)

        return expr

    def _parse_keyword_send(self) -> SmalltalkExpression:
        """Parse keyword message send."""
        receiver = self._parse_binary_send()

        # Check for keyword message
        if self._match(TokenType.KEYWORD):
            selector_parts = []
            arguments = []

            while self._match(TokenType.KEYWORD):
                keyword = self._advance().value
                selector_parts.append(keyword)
                arg = self._parse_binary_send()
                if arg is None:
                    raise SyntaxError(f"Expected argument after keyword {keyword}")
                arguments.append(arg)

            selector = "".join(selector_parts)
            return MessageSend(receiver, selector, arguments)

        return receiver

    def _parse_binary_send(self) -> SmalltalkExpression:
        """Parse binary message send."""
        left = self._parse_unary_send()

        while self._match(TokenType.BINARY_SELECTOR):
            operator = self._advance().value
            right = self._parse_unary_send()
            left = MessageSend(left, operator, [right])

        return left

    def _parse_unary_send(self) -> SmalltalkExpression:
        """Parse unary message send."""
        receiver = self._parse_primary()

        while self._match(TokenType.IDENTIFIER):
            # Check if this is really a unary message (not followed by :)
            if self._peek().type != TokenType.COLON:
                selector = self._advance().value
                receiver = MessageSend(receiver, selector, [])
            else:
                break

        return receiver

    def _parse_primary(self) -> SmalltalkExpression:
        """Parse primary expression: literal | variable | block.

        Also handles parenthesized expression.
        """
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._advance().value)

        elif self._match(
            TokenType.NIL,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.SELF,
            TokenType.SUPER,
            TokenType.THISCONTEXT,
        ):
            token = self._advance()
            if token.type == TokenType.NIL:
                return Literal(None)
            elif token.type == TokenType.TRUE:
                return Literal(True)
            elif token.type == TokenType.FALSE:
                return Literal(False)
            else:  # SELF, SUPER, THISCONTEXT
                return Variable(token.value)

        elif self._match(TokenType.NUMBER):
            value = self._advance().value
            return Literal(self._parse_number_literal(value))

        elif self._match(TokenType.STRING):
            value = self._advance().value[1:-1]  # Remove quotes
            # Handle escaped quotes
            value = value.replace("''", "'")
            return Literal(value)

        elif self._match(TokenType.CHARACTER):
            value = self._advance().value[1]  # Remove $
            return Literal(value)

        elif self._match(TokenType.SYMBOL):
            value = self._advance().value[1:]  # Remove #
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("''", "'")
            return Literal(value)

        elif self._match(TokenType.LBRACKET):
            return self._parse_block()

        elif self._match(TokenType.LPAREN):
            self._advance()  # consume (
            # Allow full expression parsing including assignment and cascade
            if self._is_assignment():
                expr = self._parse_assignment()
            else:
                expr = self._parse_cascade()
            self._consume(TokenType.RPAREN)
            if expr is None:
                raise SyntaxError("Expected expression inside parentheses")
            return expr

        elif self._match(TokenType.LBRACE):
            return self._parse_dynamic_array()

        elif self._match(TokenType.LPARRAY):
            return self._parse_literal_array()

        elif self._match(TokenType.LBARRAY):
            return self._parse_byte_array()

        else:
            # Unexpected token
            token = self._current_token()
            raise SyntaxError(
                f"Line {token.line}, Column {token.column}: "
                f"Unexpected token {token.type}"
            )

    def _parse_block(self) -> Block:
        """Parse block: [ parameters? | temporaries? body ]."""
        self._consume(TokenType.LBRACKET)

        parameters = []
        # Parse block parameters if present
        while self._match(TokenType.COLON):
            self._advance()  # consume :
            param = self._consume(TokenType.IDENTIFIER).value
            parameters.append(param)

        # If we have parameters, expect | separator
        if parameters and self._match(TokenType.PIPE):
            self._advance()

        # Parse block body (which may include temporaries)
        body = None
        if not self._match(TokenType.RBRACKET, TokenType.EOF):
            # Parse temporaries and statements separately for blocks
            temporaries = None
            statements = []

            # Check if we have temporaries (another | after parameters)
            if self._match(TokenType.PIPE):
                temporaries = self._parse_temporaries()

            # Parse statements
            statements = self._parse_statements()

            body = SmalltalkSequence(temporaries, statements)

        if self._match(TokenType.EOF):
            raise SyntaxError("Unclosed block - missing ']'")

        self._consume(TokenType.RBRACKET)
        return Block(parameters, body)

    def _parse_dynamic_array(self) -> DynamicArray:
        """Parse dynamic array: { expressions }."""
        self._consume(TokenType.LBRACE)

        expressions = []
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            expr = self._parse_expression()
            if expr:
                expressions.append(expr)

            if self._match(TokenType.PERIOD):
                self._advance()
            elif not self._match(TokenType.RBRACE):
                break

        self._consume(TokenType.RBRACE)
        return DynamicArray(expressions)

    def _parse_literal_array(self) -> LiteralArray:
        """Parse literal array: #( elements )."""
        self._consume(TokenType.LPARRAY)

        elements = []
        while not self._match(TokenType.RPAREN, TokenType.EOF):
            if self._match(TokenType.NUMBER):
                value = self._advance().value
                elements.append(self._parse_number_literal(value))
            elif self._match(TokenType.STRING):
                value = self._advance().value[1:-1].replace("''", "'")
                elements.append(value)
            elif self._match(TokenType.CHARACTER):
                value = self._advance().value[1]  # Remove $
                elements.append(value)
            elif self._match(TokenType.SYMBOL):
                value = self._advance().value[1:]
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1].replace("''", "'")
                elements.append(value)
            elif self._match(TokenType.IDENTIFIER) or self._match(
                TokenType.BINARY_SELECTOR
            ):
                elements.append(self._advance().value)
            elif self._match(TokenType.LPARRAY):
                # Nested literal array
                nested = self._parse_literal_array()
                elements.append(nested.elements)
            elif self._match(TokenType.TRUE):
                self._advance()
                elements.append(True)
            elif self._match(TokenType.FALSE):
                self._advance()
                elements.append(False)
            elif self._match(TokenType.NIL):
                self._advance()
                elements.append(None)
            elif self._match(TokenType.SELF):
                self._advance()
                elements.append("self")
            elif self._match(TokenType.SUPER):
                self._advance()
                elements.append("super")
            elif self._match(TokenType.THISCONTEXT):
                self._advance()
                elements.append("thisContext")
            else:
                break

        self._consume(TokenType.RPAREN)
        return LiteralArray(elements)

    def _parse_byte_array(self) -> ByteArray:
        """Parse byte array: #[ integers ]."""
        self._consume(TokenType.LBARRAY)

        values = []
        while not self._match(TokenType.RBRACKET, TokenType.EOF):
            if self._match(TokenType.NUMBER):
                value_str = self._advance().value
                try:
                    value = int(value_str)
                    if 0 <= value <= 255:
                        values.append(value)
                    else:
                        raise SyntaxError(f"Byte value must be 0-255, got {value}")
                except ValueError as e:
                    raise SyntaxError(f"Invalid byte value: {value_str}") from e
            else:
                break

        self._consume(TokenType.RBRACKET)
        return ByteArray(values)

    def _parse_message(self) -> tuple[str, list[SmalltalkExpression]]:
        """Parse message (selector + arguments) for cascade."""
        if self._match(TokenType.IDENTIFIER):
            selector = self._advance().value
            return selector, []
        elif self._match(TokenType.BINARY_SELECTOR):
            selector = self._advance().value
            arg = self._parse_unary_send()
            return selector, [arg]
        elif self._match(TokenType.KEYWORD):
            selector_parts = []
            arguments = []

            while self._match(TokenType.KEYWORD):
                keyword = self._advance().value
                selector_parts.append(keyword)
                arg = self._parse_binary_send()
                arguments.append(arg)

            selector = "".join(selector_parts)
            return selector, arguments
        else:
            raise SyntaxError("Expected message selector")

    def _parse_number_literal(self, value: str) -> int | float:
        """Parse number literal with support for radix and scaled decimals.

        Supports:
        - Regular integers: 123
        - Regular floats: 123.45, 1.23e4
        - Radix integers: 16rFF, 2r1010, -16r100
        - Scaled decimals: 3.14s2
        """
        # Radix integer: 16rFF, 2r1010, -16r100
        if "r" in value:
            parts = value.split("r")
            if len(parts) == 2:
                base_part = parts[0]
                digits = parts[1]
                # Handle negative sign
                is_negative = base_part.startswith("-")
                base = int(base_part[1:]) if is_negative else int(base_part)
                try:
                    result = int(digits, base)
                    return -result if is_negative else result
                except ValueError as e:
                    raise SyntaxError(f"Invalid radix number: {value}") from e

        # Scaled decimal: 3.14s2
        if "s" in value:
            parts = value.split("s")
            if len(parts) == 2:
                number_part = parts[0]
                # scale_part = parts[1] if parts[1] else "0"  # Future enhancement
                try:
                    # For now, treat as float - could be enhanced for precise decimal
                    return float(number_part)
                except ValueError as e:
                    raise SyntaxError(f"Invalid scaled decimal: {value}") from e

        # Regular float with exponential notation or decimal point
        if "." in value or "e" in value.lower():
            try:
                return float(value)
            except ValueError as e:
                raise SyntaxError(f"Invalid float: {value}") from e

        # Regular integer
        try:
            return int(value)
        except ValueError as e:
            raise SyntaxError(f"Invalid integer: {value}") from e

    def _is_reserved_identifier(self, name: str) -> bool:
        """Check if identifier is reserved and cannot be used as variable name."""
        return name in ["nil", "true", "false", "self", "super", "thisContext"]

    def _validate_bindable_identifier(self, name: str) -> None:
        """Validate that identifier can be used as variable name."""
        if self._is_reserved_identifier(name):
            raise SyntaxError(
                f"Cannot use reserved identifier '{name}' as variable name"
            )


def parse_smalltalk_method_body(method_body: str) -> SmalltalkSequence:
    """Parse a Smalltalk method body and return the AST.

    Args:
        method_body: The Smalltalk method body as a string

    Returns:
        SmalltalkSequence: The parsed AST

    Raises:
        SyntaxError: If the method body contains syntax errors

    """
    parser = SmalltalkParser()
    return parser.parse(method_body)
