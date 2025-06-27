"""Test ANSI Smalltalk features implementation."""

import pytest

from tonel_smalltalk_parser.smalltalk_parser import (
    ByteArray,
    Literal,
    SmalltalkLexer,
    SmalltalkParser,
    TokenType,
    Variable,
)


class TestANSISmalltalkFeatures:
    """Test ANSI Smalltalk compatibility features."""

    def test_radix_integers(self):
        """Test radix integer parsing."""
        parser = SmalltalkParser()

        # Test various radix integers
        test_cases = [
            ("16rFF", 255),
            ("2r1010", 10),
            ("8r777", 511),
            ("10r123", 123),
        ]

        for code, expected in test_cases:
            result = parser.parse(code)
            assert len(result.statements) == 1
            assert isinstance(result.statements[0], Literal)
            assert result.statements[0].value == expected

    def test_scaled_decimals(self):
        """Test scaled decimal parsing."""
        parser = SmalltalkParser()

        # Test scaled decimals (treated as floats for now)
        test_cases = [
            ("3.14s2", 3.14),
            ("123.456s3", 123.456),
            ("1.0s", 1.0),
        ]

        for code, expected in test_cases:
            result = parser.parse(code)
            assert len(result.statements) == 1
            assert isinstance(result.statements[0], Literal)
            assert abs(result.statements[0].value - expected) < 0.001

    def test_thiscontext_pseudovariable(self):
        """Test thisContext pseudo-variable."""
        parser = SmalltalkParser()

        result = parser.parse("thisContext")
        assert len(result.statements) == 1
        assert isinstance(result.statements[0], Variable)
        assert result.statements[0].name == "thisContext"

    def test_thiscontext_tokenization(self):
        """Test thisContext tokenization."""
        lexer = SmalltalkLexer()

        tokens = lexer.tokenize("thisContext")
        token_types = [t.type for t in tokens if t.type != TokenType.EOF]

        assert token_types == [TokenType.THISCONTEXT]

    def test_byte_array_literals(self):
        """Test byte array literal parsing."""
        parser = SmalltalkParser()

        # Test valid byte arrays
        test_cases = [
            ("#[1 2 3]", [1, 2, 3]),
            ("#[0 255]", [0, 255]),
            ("#[]", []),
            ("#[42]", [42]),
        ]

        for code, expected in test_cases:
            result = parser.parse(code)
            assert len(result.statements) == 1
            assert isinstance(result.statements[0], ByteArray)
            assert result.statements[0].values == expected

    def test_byte_array_validation(self):
        """Test byte array value validation."""
        parser = SmalltalkParser()

        # Test invalid byte values
        with pytest.raises(SyntaxError, match="Byte value must be 0-255"):
            parser.parse("#[256]")

        with pytest.raises(SyntaxError, match="Byte value must be 0-255"):
            parser.parse("#[-1]")

    def test_reserved_identifier_validation(self):
        """Test reserved identifier validation."""
        parser = SmalltalkParser()

        # Test assignment to reserved identifiers (should fail)
        reserved_identifiers = ["nil", "true", "false", "self", "super", "thisContext"]

        for reserved in reserved_identifiers:
            with pytest.raises(
                SyntaxError, match=f"Cannot use reserved identifier '{reserved}'"
            ):
                parser.parse(f"{reserved} := 42")

    def test_reserved_identifier_in_temporaries(self):
        """Test reserved identifiers in temporary variables."""
        parser = SmalltalkParser()

        # Test temporaries with reserved identifiers (should fail)
        with pytest.raises(SyntaxError, match="Cannot use reserved identifier 'nil'"):
            parser.parse("| nil | nil := 42")

        with pytest.raises(SyntaxError, match="Cannot use reserved identifier 'self'"):
            parser.parse("| self | self inspect")

    def test_complex_radix_expressions(self):
        """Test complex expressions with radix integers."""
        parser = SmalltalkParser()

        # Test arithmetic with radix integers
        result = parser.parse("16rFF + 2r1010")
        assert len(result.statements) == 1
        # Should parse as a binary message send

    def test_mixed_number_types(self):
        """Test mixing different number types."""
        parser = SmalltalkParser()

        # Test sequence with different number types
        result = parser.parse("123. 16rFF. 3.14s2. 1.23e4")
        assert len(result.statements) == 4

        # Check first statement (regular integer)
        assert isinstance(result.statements[0], Literal)
        assert result.statements[0].value == 123

        # Check second statement (radix integer)
        assert isinstance(result.statements[1], Literal)
        assert result.statements[1].value == 255

    def test_ansi_features_in_blocks(self):
        """Test ANSI features work inside blocks."""
        parser = SmalltalkParser()

        # Test radix integer in block
        result = parser.parse("[ 16rFF ]")
        assert len(result.statements) == 1
        # Block should contain the radix integer

        # Test thisContext in block
        result = parser.parse("[ thisContext ]")
        assert len(result.statements) == 1
        # Block should contain thisContext reference
