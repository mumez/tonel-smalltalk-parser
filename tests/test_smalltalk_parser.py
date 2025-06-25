"""Tests for the Smalltalk method body parser."""

import pytest

from src.tonel_smalltalk_parser.smalltalk_parser import (
    Assignment,
    Block,
    Cascade,
    DynamicArray,
    Literal,
    LiteralArray,
    MessageSend,
    Return,
    SmalltalkLexer,
    SmalltalkParser,
    SmalltalkSequence,
    TemporaryVariables,
    TokenType,
    Variable,
    parse_smalltalk_method_body,
)


class TestSmalltalkLexer:
    """Test cases for the Smalltalk lexer."""

    def test_simple_tokens(self):
        """Test tokenization of simple tokens."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize("^ self")

        expected_types = [TokenType.RETURN, TokenType.SELF, TokenType.EOF]
        actual_types = [token.type for token in tokens]
        assert actual_types == expected_types

    def test_string_literals(self):
        """Test string literal tokenization."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize("'hello world' 'it''s escaped'")

        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        assert len(string_tokens) == 2
        assert string_tokens[0].value == "'hello world'"
        assert string_tokens[1].value == "'it''s escaped'"

    def test_numbers(self):
        """Test number tokenization."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize("42 3.14 -5 1.5e-10")

        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        assert len(number_tokens) == 4
        assert number_tokens[0].value == "42"
        assert number_tokens[1].value == "3.14"
        assert number_tokens[2].value == "-5"
        assert number_tokens[3].value == "1.5e-10"

    def test_symbols(self):
        """Test symbol tokenization."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize("#symbol #'symbol with spaces'")

        symbol_tokens = [t for t in tokens if t.type == TokenType.SYMBOL]
        assert len(symbol_tokens) == 2
        assert symbol_tokens[0].value == "#symbol"
        assert symbol_tokens[1].value == "#'symbol with spaces'"

    def test_comments(self):
        """Test comment tokenization."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize('"this is a comment" "with ""quotes"""')

        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
        assert len(comment_tokens) == 2
        assert comment_tokens[0].value == '"this is a comment"'
        assert comment_tokens[1].value == '"with ""quotes"""'

    def test_keywords_and_identifiers(self):
        """Test keyword and identifier tokenization."""
        lexer = SmalltalkLexer()
        tokens = lexer.tokenize("at: put: value initialize")

        non_eof_tokens = [t for t in tokens if t.type != TokenType.EOF]
        expected_types = [
            TokenType.KEYWORD,
            TokenType.KEYWORD,
            TokenType.IDENTIFIER,
            TokenType.IDENTIFIER,
        ]
        actual_types = [t.type for t in non_eof_tokens]
        assert actual_types == expected_types

        assert non_eof_tokens[0].value == "at:"
        assert non_eof_tokens[1].value == "put:"
        assert non_eof_tokens[2].value == "value"
        assert non_eof_tokens[3].value == "initialize"

    def test_binary_selectors(self):
        """Test binary selector tokenization."""
        lexer = SmalltalkLexer()
        # Test binary selectors in context where they would be used
        tokens = lexer.tokenize("a + b - c * d / e = f > g < h >= i <= j ~= k & l | m")

        binary_tokens = [t for t in tokens if t.type == TokenType.BINARY_SELECTOR]
        expected_values = [
            "+",
            "-",
            "*",
            "/",
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "~=",
            "&",
            "|",
        ]
        actual_values = [t.value for t in binary_tokens]
        assert actual_values == expected_values


class TestSmalltalkParser:
    """Test cases for the Smalltalk parser."""

    def test_simple_return(self):
        """Test parsing a simple return statement."""
        parser = SmalltalkParser()
        ast = parser.parse("^ 42")

        assert isinstance(ast, SmalltalkSequence)
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Return)
        assert isinstance(ast.statements[0].expression, Literal)
        assert ast.statements[0].expression.value == 42

    def test_temporary_variables(self):
        """Test parsing temporary variables."""
        parser = SmalltalkParser()
        ast = parser.parse("| x y z | x := 1")

        assert isinstance(ast.temporaries, TemporaryVariables)
        assert ast.temporaries.variables == ["x", "y", "z"]
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)

    def test_assignment(self):
        """Test parsing assignment."""
        parser = SmalltalkParser()
        ast = parser.parse("x := 42")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, Assignment)
        assert stmt.variable == "x"
        assert isinstance(stmt.value, Literal)
        assert stmt.value.value == 42

    def test_unary_message(self):
        """Test parsing unary message."""
        parser = SmalltalkParser()
        ast = parser.parse("self initialize")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, MessageSend)
        assert isinstance(stmt.receiver, Variable)
        assert stmt.receiver.name == "self"
        assert stmt.selector == "initialize"
        assert stmt.arguments == []

    def test_binary_message(self):
        """Test parsing binary message."""
        parser = SmalltalkParser()
        ast = parser.parse("1 + 2")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, MessageSend)
        assert isinstance(stmt.receiver, Literal)
        assert stmt.receiver.value == 1
        assert stmt.selector == "+"
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], Literal)
        assert stmt.arguments[0].value == 2

    def test_keyword_message(self):
        """Test parsing keyword message."""
        parser = SmalltalkParser()
        ast = parser.parse("dict at: 'key' put: 'value'")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, MessageSend)
        assert isinstance(stmt.receiver, Variable)
        assert stmt.receiver.name == "dict"
        assert stmt.selector == "at:put:"
        assert len(stmt.arguments) == 2
        assert isinstance(stmt.arguments[0], Literal)
        assert stmt.arguments[0].value == "key"
        assert isinstance(stmt.arguments[1], Literal)
        assert stmt.arguments[1].value == "value"

    def test_cascade(self):
        """Test parsing cascade."""
        parser = SmalltalkParser()
        ast = parser.parse("stream nextPut: 'a'; nextPut: 'b'")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, Cascade)
        assert isinstance(stmt.receiver, Variable)
        assert stmt.receiver.name == "stream"
        assert len(stmt.messages) == 2  # Both messages are in the cascade

        # First message (stream nextPut: 'a')
        selector1, args1 = stmt.messages[0]
        assert selector1 == "nextPut:"
        assert len(args1) == 1
        assert isinstance(args1[0], Literal)
        assert args1[0].value == "a"

        # Second message (; nextPut: 'b')
        selector2, args2 = stmt.messages[1]
        assert selector2 == "nextPut:"
        assert len(args2) == 1
        assert isinstance(args2[0], Literal)
        assert args2[0].value == "b"

    def test_block_simple(self):
        """Test parsing simple block."""
        parser = SmalltalkParser()
        ast = parser.parse("[ 1 + 2 ]")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, Block)
        assert stmt.parameters == []
        assert isinstance(stmt.body, SmalltalkSequence)
        assert len(stmt.body.statements) == 1

    def test_block_with_parameters(self):
        """Test parsing block with parameters."""
        parser = SmalltalkParser()
        ast = parser.parse("[ :x :y | x + y ]")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, Block)
        assert stmt.parameters == ["x", "y"]
        assert isinstance(stmt.body, SmalltalkSequence)
        assert len(stmt.body.statements) == 1

    def test_literal_array(self):
        """Test parsing literal array."""
        parser = SmalltalkParser()
        ast = parser.parse("#(1 2 'hello' #symbol)")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, LiteralArray)
        assert stmt.elements == [1, 2, "hello", "symbol"]

    def test_dynamic_array(self):
        """Test parsing dynamic array."""
        parser = SmalltalkParser()
        ast = parser.parse("{ 1 + 2. 'hello' }")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, DynamicArray)
        assert len(stmt.expressions) == 2

    def test_complex_method(self):
        """Test parsing complex method with multiple elements."""
        parser = SmalltalkParser()
        method_body = """
        | temp result |
        temp := self getValue.
        result := temp + 42.
        ^ result
        """
        ast = parser.parse(method_body)

        # Check temporaries
        assert isinstance(ast.temporaries, TemporaryVariables)
        assert ast.temporaries.variables == ["temp", "result"]

        # Check statements
        assert len(ast.statements) == 3

        # First assignment
        stmt1 = ast.statements[0]
        assert isinstance(stmt1, Assignment)
        assert stmt1.variable == "temp"

        # Second assignment
        stmt2 = ast.statements[1]
        assert isinstance(stmt2, Assignment)
        assert stmt2.variable == "result"

        # Return statement
        stmt3 = ast.statements[2]
        assert isinstance(stmt3, Return)
        assert isinstance(stmt3.expression, Variable)
        assert stmt3.expression.name == "result"

    def test_nested_blocks(self):
        """Test parsing nested blocks."""
        parser = SmalltalkParser()
        ast = parser.parse("[ [ 1 + 2 ] value ] value")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, MessageSend)
        assert isinstance(stmt.receiver, Block)

        # Check inner block
        outer_block = stmt.receiver
        inner_stmt = outer_block.body.statements[0]
        assert isinstance(inner_stmt, MessageSend)
        assert isinstance(inner_stmt.receiver, Block)

    def test_character_literals(self):
        """Test parsing character literals."""
        parser = SmalltalkParser()
        ast = parser.parse("$a")

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, Literal)
        assert stmt.value == "a"

    def test_pseudo_variables(self):
        """Test parsing pseudo variables."""
        parser = SmalltalkParser()
        ast = parser.parse("nil. true. false. self. super")

        assert len(ast.statements) == 5

        # nil
        assert isinstance(ast.statements[0], Literal)
        assert ast.statements[0].value is None

        # true
        assert isinstance(ast.statements[1], Literal)
        assert ast.statements[1].value is True

        # false
        assert isinstance(ast.statements[2], Literal)
        assert ast.statements[2].value is False

        # self
        assert isinstance(ast.statements[3], Variable)
        assert ast.statements[3].name == "self"

        # super
        assert isinstance(ast.statements[4], Variable)
        assert ast.statements[4].name == "super"


class TestIntegration:
    """Integration tests for the complete parsing pipeline."""

    def test_parse_smalltalk_method_body_function(self):
        """Test the convenience function."""
        method_body = "^ self class name"
        ast = parse_smalltalk_method_body(method_body)

        assert isinstance(ast, SmalltalkSequence)
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Return)

    def test_real_smalltalk_methods(self):
        """Test parsing real Smalltalk method examples."""
        # Example 1: Simple getter
        method1 = "^ value"
        ast1 = parse_smalltalk_method_body(method1)
        assert isinstance(ast1.statements[0], Return)

        # Example 2: Simple setter
        method2 = "value := anObject"
        ast2 = parse_smalltalk_method_body(method2)
        assert isinstance(ast2.statements[0], Assignment)

        # Example 3: Method with temporaries and multiple statements
        method3 = """
        | x y |
        x := 10.
        y := x + 5.
        ^ y * 2
        """
        ast3 = parse_smalltalk_method_body(method3)
        assert len(ast3.temporaries.variables) == 2
        assert len(ast3.statements) == 3

        # Example 4: Block iteration
        method4 = "collection do: [ :each | each printOn: stream ]"
        ast4 = parse_smalltalk_method_body(method4)
        stmt = ast4.statements[0]
        assert isinstance(stmt, MessageSend)
        assert stmt.selector == "do:"
        assert isinstance(stmt.arguments[0], Block)
        assert stmt.arguments[0].parameters == ["each"]

    def test_error_handling(self):
        """Test error handling for invalid syntax."""
        with pytest.raises(SyntaxError):
            parse_smalltalk_method_body("^ [")  # Unclosed bracket

        with pytest.raises(SyntaxError):
            parse_smalltalk_method_body("x := ")  # Incomplete assignment

    def test_empty_method(self):
        """Test parsing empty method body."""
        ast = parse_smalltalk_method_body("")
        assert isinstance(ast, SmalltalkSequence)
        assert ast.temporaries is None
        assert len(ast.statements) == 0

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        method_with_whitespace = """

        | x |

        x := 42.

        ^ x

        """
        ast = parse_smalltalk_method_body(method_with_whitespace)
        assert len(ast.temporaries.variables) == 1
        assert len(ast.statements) == 2


if __name__ == "__main__":
    pytest.main([__file__])
