"""Test cases for Tonel parser functionality."""

import pytest

from tonel_smalltalk_parser import (
    ClassDefinition,
    MethodDefinition,
    TonelFile,
    TonelParser,
)


class TestTonelParser:
    """Test cases for the TonelParser class."""

    def setup_method(self):
        """Setup for each test method."""
        self.parser = TonelParser()

    def test_parser_initialization(self):
        """Test parser can be initialized."""
        assert self.parser is not None
        assert hasattr(self.parser, "parse")

    def test_simple_class_definition(self):
        """Test parsing a simple class definition."""
        tonel_content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}"""

        result = self.parser.parse(tonel_content)

        assert isinstance(result, TonelFile)
        assert result.class_definition.type == "Class"
        assert result.class_definition.metadata is not None
        assert result.methods == []
        assert result.comment is None

    def test_class_with_comment(self):
        """Test parsing class with comment."""
        tonel_content = """"A sample class for demonstration"
Class {
    #name : #Counter,
    #superclass : #Object
}"""

        result = self.parser.parse(tonel_content)

        assert isinstance(result, TonelFile)
        assert result.comment == "A sample class for demonstration"
        assert result.class_definition.type == "Class"

    def test_trait_definition(self):
        """Test parsing a trait definition."""
        tonel_content = """Trait {
    #name : #TCountable,
    #category : #'Demo-Traits'
}"""

        result = self.parser.parse(tonel_content)

        assert isinstance(result, TonelFile)
        assert result.class_definition.type == "Trait"

    def test_extension_definition(self):
        """Test parsing an extension definition."""
        tonel_content = """Extension {
    #name : #String
}"""

        result = self.parser.parse(tonel_content)

        assert isinstance(result, TonelFile)
        assert result.class_definition.type == "Extension"

    def test_method_with_unary_selector(self):
        """Test parsing method with unary selector."""
        tonel_content = """Class {
    #name : #Counter
}

{ #category : #accessing }
Counter >> value [
    ^ value
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.class_name == "Counter"
        assert method.selector == "value"
        assert method.is_class_method is False
        assert "^ value" in method.body.strip()
        assert method.metadata is not None

    def test_method_with_keyword_selector(self):
        """Test parsing method with keyword selector."""
        tonel_content = """Class {
    #name : #Counter
}

{ #category : #accessing }
Counter >> value: anInteger [
    value := anInteger
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.class_name == "Counter"
        assert method.selector == "value:"
        assert method.is_class_method is False
        assert "value := anInteger" in method.body.strip()

    def test_method_with_binary_selector(self):
        """Test parsing method with binary selector."""
        tonel_content = """Class {
    #name : #Counter
}

{ #category : #arithmetic }
Counter >> + aNumber [
    ^ self value + aNumber
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.class_name == "Counter"
        assert method.selector == "+"
        assert method.is_class_method is False

    def test_class_method(self):
        """Test parsing class method."""
        tonel_content = """Class {
    #name : #Counter
}

{ #category : #'class side' }
Counter class >> new [
    ^ super new initialize
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.class_name == "Counter"
        assert method.selector == "new"
        assert method.is_class_method is True

    def test_multiple_methods(self):
        """Test parsing multiple methods."""
        tonel_content = """Class {
    #name : #Counter
}

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
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 3
        selectors = [method.selector for method in result.methods]
        assert "value" in selectors
        assert "value:" in selectors
        assert "+" in selectors

    def test_method_with_complex_body(self):
        """Test parsing method with complex Smalltalk code including blocks."""
        tonel_content = """Class {
    #name : #Counter
}

{ #category : #examples }
Counter >> complexMethod [
    | block result |
    block := [ :x | x + 1 ].
    result := block value: 5.
    ^ result
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.selector == "complexMethod"
        assert "[ :x | x + 1 ]" in method.body
        assert "block value: 5" in method.body

    def test_ston_metadata_parsing(self):
        """Test parsing STON metadata in class definition."""
        tonel_content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #instVars : [ 'value', 'count' ],
    #category : #'Demo-Core'
}"""

        result = self.parser.parse(tonel_content)

        metadata = result.class_definition.metadata
        assert metadata is not None
        # Note: Full STON parsing might need refinement

    def test_method_without_metadata(self):
        """Test parsing method without metadata."""
        tonel_content = """Class {
    #name : #Counter
}

Counter >> simpleMethod [
    ^ 42
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.metadata is None
        assert method.selector == "simpleMethod"

    def test_empty_method_body(self):
        """Test parsing method with empty body."""
        tonel_content = """Class {
    #name : #Counter
}

Counter >> emptyMethod [
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.body.strip() == ""

    def test_invalid_tonel_content(self):
        """Test parsing invalid Tonel content raises error."""
        invalid_content = """Invalid Tonel Content"""

        with pytest.raises(ValueError):
            self.parser.parse(invalid_content)


class TestTonelDataStructures:
    """Test cases for Tonel data structures."""

    def test_method_definition_creation(self):
        """Test MethodDefinition creation."""
        method = MethodDefinition(
            class_name="TestClass",
            is_class_method=False,
            selector="testMethod",
            body="^ self",
            metadata={"category": "testing"},
        )

        assert method.class_name == "TestClass"
        assert method.is_class_method is False
        assert method.selector == "testMethod"
        assert method.body == "^ self"
        assert method.metadata["category"] == "testing"

    def test_class_definition_creation(self):
        """Test ClassDefinition creation."""
        class_def = ClassDefinition(
            type="Class", metadata={"name": "TestClass", "superclass": "Object"}
        )

        assert class_def.type == "Class"
        assert class_def.metadata["name"] == "TestClass"
        assert class_def.metadata["superclass"] == "Object"

    def test_tonel_file_creation(self):
        """Test TonelFile creation."""
        class_def = ClassDefinition(type="Class", metadata={})
        method = MethodDefinition(
            class_name="Test", is_class_method=False, selector="test", body="^ nil"
        )

        tonel_file = TonelFile(
            comment="Test comment", class_definition=class_def, methods=[method]
        )

        assert tonel_file.comment == "Test comment"
        assert tonel_file.class_definition == class_def
        assert len(tonel_file.methods) == 1
        assert tonel_file.methods[0] == method


if __name__ == "__main__":
    pytest.main([__file__])
