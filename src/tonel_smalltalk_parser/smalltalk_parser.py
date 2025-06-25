"""Smalltalk method body parser implementation.
Based on the BNF grammar specification in doc/tonel-and-smalltalk-bnf.md.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Optional


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

    # Operators
    ASSIGN = "ASSIGN"  # :=
    RETURN = "RETURN"  # ^
    CASCADE = "CASCADE"  # ;
    PERIOD = "PERIOD"  # .
    PIPE = "PIPE"  # |
    COLON = "COLON"  # :

    # Special
    COMMENT = "COMMENT"
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
            (TokenType.STRING, r"'([^']|'')*'"),
            (TokenType.CHARACTER, r"\$\S"),
            (TokenType.LPARRAY, r"#\("),
            (TokenType.SYMBOL, r"#[a-zA-Z][a-zA-Z0-9_]*|#\'([^\']|\'\')*\'"),
            (TokenType.NUMBER, r"[+-]?\d+(\.\d+)?([eE][+-]?\d+)?"),
            (TokenType.ASSIGN, r":="),
            (TokenType.RETURN, r"\^"),
            (TokenType.CASCADE, r";"),
            (TokenType.PERIOD, r"\."),
            (TokenType.PIPE, r"\|"),  # Keep this before binary selector
            (TokenType.COLON, r":"),
            (TokenType.LPAREN, r"\("),
            (TokenType.RPAREN, r"\)"),
            (TokenType.LBRACKET, r"\["),
            (TokenType.RBRACKET, r"\]"),
            (TokenType.LBRACE, r"\{"),
            (TokenType.RBRACE, r"\}"),
            (TokenType.KEYWORD, r"[a-zA-Z][a-zA-Z0-9_]*:"),
            (TokenType.IDENTIFIER, r"[a-zA-Z][a-zA-Z0-9_]*"),
            (TokenType.BINARY_SELECTOR, r"[\\+*\/=><@%~&\-?]+"),  # Remove | from here
            (TokenType.WHITESPACE, r"\s+"),
        ]

        # Compile patterns
        self.compiled_patterns = [
            (token_type, re.compile(pattern))
            for token_type, pattern in self.token_patterns
        ]

        # Keywords
        self.keywords = {
            "nil": TokenType.NIL,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "self": TokenType.SELF,
            "super": TokenType.SUPER,
        }

    def tokenize(self, text: str) -> list[Token]:
        """Tokenize Smalltalk source code."""
        tokens = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            col = 0
            while col < len(line):
                # Try to match each pattern
                matched = False
                for token_type, pattern in self.compiled_patterns:
                    match = pattern.match(line, col)
                    if match:
                        value = match.group(0)

                        # Skip whitespace tokens
                        if token_type != TokenType.WHITESPACE:
                            # Check for keywords
                            if (
                                token_type == TokenType.IDENTIFIER
                                and value in self.keywords
                            ):
                                token_type = self.keywords[value]

                            # Check if | should be treated as binary selector
                            # This is a simplified approach - in real Smalltalk, context matters more
                            if token_type == TokenType.PIPE and self._is_binary_context(
                                tokens, value
                            ):
                                token_type = TokenType.BINARY_SELECTOR

                            tokens.append(Token(token_type, value, line_num, col + 1))

                        col = match.end()
                        matched = True
                        break

                if not matched:
                    # Skip unknown characters
                    col += 1

        tokens.append(
            Token(TokenType.EOF, "", len(lines), len(lines[-1]) if lines else 0)
        )
        return tokens

    def _is_binary_context(self, tokens: list[Token], value: str) -> bool:
        """Determine if | should be treated as a binary selector based on context.
        This is a simplified heuristic.
        """
        if not tokens:
            return False

        # Look for unclosed brackets and pipes to understand context
        bracket_count = 0
        pipe_count = 0
        colon_count = 0

        # Scan from the end to understand the current context
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]
            if token.type == TokenType.RBRACKET:
                bracket_count += 1
            elif token.type == TokenType.LBRACKET:
                bracket_count -= 1
                if bracket_count < 0:
                    # We're inside a block
                    # Count colons and pipes since this opening bracket
                    for j in range(i + 1, len(tokens)):
                        if tokens[j].type == TokenType.COLON:
                            colon_count += 1
                        elif tokens[j].type == TokenType.PIPE:
                            pipe_count += 1

                    # If we have colons but no pipes, this | separates parameters from body
                    if colon_count > 0 and pipe_count == 0:
                        return False
                    break
            elif token.type == TokenType.PIPE:
                pipe_count += 1

        # General case: look for unclosed pipes (temporary variables)
        all_pipe_count = sum(1 for t in tokens if t.type == TokenType.PIPE)
        if all_pipe_count % 2 == 1:
            # We have an unclosed pipe, so this | closes temporaries
            return False

        # Look at the last token
        last_token = tokens[-1]

        # If the last token could be a receiver (identifier, literal, etc.)
        # then | is likely a binary selector
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
        ]


class SmalltalkParser:
    """Parser for Smalltalk method bodies."""

    def __init__(self):
        self.lexer = SmalltalkLexer()
        self.tokens = []
        self.current = 0

    def parse(self, method_body: str) -> SmalltalkSequence:
        """Parse Smalltalk method body and return AST."""
        self.tokens = self.lexer.tokenize(method_body)
        self.current = 0
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
        return token

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
        """Parse Smalltalk sequence: temps? statements?"""
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
            if self._match(TokenType.IDENTIFIER):
                variables.append(self._advance().value)
            else:
                break

        self._consume(TokenType.PIPE, "Expected closing '|' for temporaries")
        return TemporaryVariables(variables)

    def _parse_statements(self) -> list[SmalltalkExpression]:
        """Parse sequence of statements."""
        statements = []

        while not self._match(TokenType.EOF, TokenType.RBRACKET):
            # Check for return statement
            if self._match(TokenType.RETURN):
                statements.append(self._parse_return())
                break  # Return is last statement

            # Parse expression
            expr = self._parse_expression()
            if expr:
                statements.append(expr)

            # Handle statement separator
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
        return Return(expression)

    def _parse_expression(self) -> SmalltalkExpression | None:
        """Parse expression: assignment | cascade | keywordSend | binarySend | unarySend | primary."""
        if not self._current_token() or self._match(TokenType.EOF):
            return None

        # Try assignment
        if self._is_assignment():
            return self._parse_assignment()

        # Parse message send expression
        expr = self._parse_cascade()
        return expr

    def _is_assignment(self) -> bool:
        """Check if current position is an assignment."""
        return (
            self._match(TokenType.IDENTIFIER) and self._peek().type == TokenType.ASSIGN
        )

    def _parse_assignment(self) -> Assignment:
        """Parse assignment: variable := expression."""
        variable = self._consume(TokenType.IDENTIFIER).value
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
                selector, args = self._parse_message()
                messages.append((selector, args))

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
        """Parse primary expression: literal | variable | block | parenthesized expression."""
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._advance().value)

        elif self._match(
            TokenType.NIL,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.SELF,
            TokenType.SUPER,
        ):
            token = self._advance()
            if token.type == TokenType.NIL:
                return Literal(None)
            elif token.type == TokenType.TRUE:
                return Literal(True)
            elif token.type == TokenType.FALSE:
                return Literal(False)
            else:  # SELF, SUPER
                return Variable(token.value)

        elif self._match(TokenType.NUMBER):
            value = self._advance().value
            if "." in value or "e" in value.lower():
                return Literal(float(value))
            else:
                return Literal(int(value))

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
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return expr

        elif self._match(TokenType.LBRACE):
            return self._parse_dynamic_array()

        elif self._match(TokenType.LPARRAY):
            return self._parse_literal_array()

        else:
            # Unexpected token
            token = self._current_token()
            raise SyntaxError(
                f"Line {token.line}, Column {token.column}: Unexpected token {token.type}"
            )

    def _parse_block(self) -> Block:
        """Parse block: [ parameters? | body ]."""
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

        # Parse block body
        body = None
        if not self._match(TokenType.RBRACKET, TokenType.EOF):
            statements = self._parse_statements()
            body = SmalltalkSequence(None, statements)

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
                elements.append(float(value) if "." in value else int(value))
            elif self._match(TokenType.STRING):
                value = self._advance().value[1:-1].replace("''", "'")
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
            else:
                break

        self._consume(TokenType.RPAREN)
        return LiteralArray(elements)

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
