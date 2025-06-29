"""Test cases for TonelFullParser functionality."""

import os
import tempfile

import pytest

from tonel_smalltalk_parser import TonelFile
from tonel_smalltalk_parser.tonel_full_parser import TonelFullParser


class TestTonelFullParser:
    """Test cases for the TonelFullParser class."""

    def setup_method(self):
        """Set up for each test method."""
        self.parser = TonelFullParser()

    def test_parser_initialization(self):
        """Test parser can be initialized."""
        assert self.parser is not None
        assert hasattr(self.parser, "parse")
        assert hasattr(self.parser, "validate")
        assert self.parser.tonel_parser is not None
        assert self.parser.smalltalk_parser is not None

    def test_parse_valid_tonel_with_valid_smalltalk(self):
        """Test parsing valid Tonel content with valid Smalltalk methods."""
        valid_content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> increment [
    count := count + 1
]

Counter >> value [
    ^ count
]"""
        result = self.parser.parse(valid_content)
        assert isinstance(result, TonelFile)
        assert len(result.methods) == 2

    def test_parse_invalid_smalltalk_raises_error(self):
        """Test that invalid Smalltalk syntax raises SyntaxError."""
        content_with_bad_smalltalk = """Class {
    #name : #TestClass,
    #superclass : #Object
}

TestClass >> badMethod [
    x :=
]"""
        with pytest.raises(SyntaxError) as exc_info:
            self.parser.parse(content_with_bad_smalltalk)
        assert "Invalid Smalltalk syntax" in str(exc_info.value)
        assert "TestClass>>badMethod" in str(exc_info.value)


class TestTonelFullParserValidation:
    """Test cases for TonelFullParser validation methods."""

    def setup_method(self):
        """Set up for each test method."""
        self.parser = TonelFullParser()

    def test_validate_valid_tonel_with_valid_smalltalk(self):
        """Test validate returns True for valid Tonel with valid Smalltalk."""
        valid_content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> increment [
    count := count + 1
]

Counter >> value [
    ^ count
]"""
        assert self.parser.validate(valid_content)[0] is True

    def test_validate_invalid_tonel_structure(self):
        """Test validate returns False for invalid Tonel structure."""
        invalid_tonel = "This is not valid Tonel content"
        assert self.parser.validate(invalid_tonel)[0] is False

    def test_validate_valid_tonel_invalid_smalltalk(self):
        """Test validate returns False for valid Tonel but invalid Smalltalk."""
        content_with_bad_smalltalk = """Class {
    #name : #TestClass,
    #superclass : #Object
}

TestClass >> badMethod [
    x :=
]"""
        assert self.parser.validate(content_with_bad_smalltalk)[0] is False

    def test_validate_class_only(self):
        """Test validate returns True for class definition only."""
        class_only = """Class {
    #name : #TestClass,
    #superclass : #Object
}"""
        assert self.parser.validate(class_only)[0] is True

    def test_validate_empty_content(self):
        """Test validate returns False for empty content."""
        assert self.parser.validate("")[0] is False

    def test_validate_complex_valid_content(self):
        """Test validate returns True for complex but valid content."""
        complex_content = """"A complex test class"
Class {
    #name : #ComplexClass,
    #superclass : #Object,
    #instVars : ['value', 'cache'],
    #category : #'Test-Complex'
}

ComplexClass >> initialize [
    super initialize.
    value := 0.
    cache := Dictionary new
]

ComplexClass >> setValue: anObject [
    | oldValue |
    oldValue := value.
    value := anObject.
    cache at: #oldValue put: oldValue
]

ComplexClass >> getValue [
    ^ value
]

ComplexClass >> processCollection: aCollection [
    ^ aCollection select: [ :each | each isNumber ]
        thenCollect: [ :num | num * 2 ]
]"""
        assert self.parser.validate(complex_content)[0] is True

    def test_validate_method_with_blocks(self):
        """Test validate returns True for methods with valid blocks."""
        content_with_blocks = """Class {
    #name : #BlockTest,
    #superclass : #Object
}

BlockTest >> processNumbers [
    | result |
    result := #(1 2 3 4 5) select: [ :num | num odd ]
        thenCollect: [ :odd | odd * 2 ].
    ^ result
]"""
        assert self.parser.validate(content_with_blocks)[0] is True

    def test_validate_method_with_nested_blocks(self):
        """Test validate returns True for methods with nested blocks."""
        content_with_nested = """Class {
    #name : #NestedTest,
    #superclass : #Object
}

NestedTest >> nestedExample [
    ^ collection collect: [ :item |
        item processUsing: [ :processor |
            processor transform: [ :data | data * 2 ]
        ]
    ]
]"""
        assert self.parser.validate(content_with_nested)[0] is True

    def test_validate_trait_with_methods(self):
        """Test validate returns True for trait with valid methods."""
        trait_content = """Trait {
    #name : #TComparable,
    #category : #'Test-Traits'
}

TComparable >> < other [
    ^ (self compare: other) < 0
]

TComparable >> <= other [
    ^ (self compare: other) <= 0
]"""
        assert self.parser.validate(trait_content)[0] is True

    def test_validate_extension_with_methods(self):
        """Test validate returns True for extension with valid methods."""
        extension_content = """Extension {
    #name : #Object,
    #category : #'*Test-Extensions'
}

Object >> isTest [
    ^ false
]"""
        assert self.parser.validate(extension_content)[0] is True

    def test_validate_from_file_valid(self):
        """Test validate_from_file returns True for valid file."""
        valid_content = """Class {
    #name : #TestClass,
    #superclass : #Object
}

TestClass >> test [
    ^ true
]"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(valid_content)
            f.flush()
            try:
                assert self.parser.validate_from_file(f.name)[0] is True
            finally:
                os.unlink(f.name)

    def test_validate_from_file_invalid_tonel(self):
        """Test validate_from_file returns False for invalid Tonel file."""
        invalid_content = "Invalid Tonel content"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(invalid_content)
            f.flush()
            try:
                assert self.parser.validate_from_file(f.name)[0] is False
            finally:
                os.unlink(f.name)

    def test_validate_from_file_invalid_smalltalk(self):
        """Test validate_from_file returns False for invalid Smalltalk in file."""
        content_with_bad_smalltalk = """Class {
    #name : #TestClass,
    #superclass : #Object
}

TestClass >> badMethod [
    x :=
]"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content_with_bad_smalltalk)
            f.flush()
            try:
                assert self.parser.validate_from_file(f.name)[0] is False
            finally:
                os.unlink(f.name)

    def test_validate_from_file_nonexistent(self):
        """Test validate_from_file returns False for nonexistent file."""
        assert self.parser.validate_from_file("/nonexistent/file.st")[0] is False

    def test_parse_from_file_valid(self):
        """Test parse_from_file works for valid file."""
        valid_content = """Class {
    #name : #FileTest,
    #superclass : #Object
}

FileTest >> test [
    ^ 'from file'
]"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(valid_content)
            f.flush()
            try:
                result = self.parser.parse_from_file(f.name)
                assert isinstance(result, TonelFile)
                assert len(result.methods) == 1
                assert result.methods[0].selector == "test"
            finally:
                os.unlink(f.name)

    def test_parse_from_file_invalid_smalltalk_raises_error(self):
        """Test parse_from_file raises SyntaxError for invalid Smalltalk."""
        content_with_bad_smalltalk = """Class {
    #name : #TestClass,
    #superclass : #Object
}

TestClass >> badMethod [
    x :=
]"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content_with_bad_smalltalk)
            f.flush()
            try:
                with pytest.raises(SyntaxError):
                    self.parser.parse_from_file(f.name)
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])
