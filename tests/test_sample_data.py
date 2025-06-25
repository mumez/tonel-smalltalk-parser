"""Test cases using sample Tonel data from the BNF specification."""

import pytest

from tonel_smalltalk_parser import TonelParser


class TestSampleTonelData:
    """Test cases using the sample Tonel code from the BNF specification."""

    def setup_method(self):
        """Setup for each test method."""
        self.parser = TonelParser()

    def test_bnf_specification_sample(self):
        """Test parsing the sample code from the BNF specification."""
        # Sample from tonel-and-smalltalk-bnf.md
        sample_tonel = """"A sample class for demonstration"
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
]"""

        result = self.parser.parse(sample_tonel)

        # Test comment
        assert result.comment == "A sample class for demonstration"

        # Test class definition
        assert result.class_definition.type == "Class"

        # Test methods count
        assert len(result.methods) == 5

        # Test specific methods
        method_selectors = [method.selector for method in result.methods]
        expected_selectors = ["initialize", "value", "value:", "+", "new"]

        for selector in expected_selectors:
            assert selector in method_selectors

        # Test class method detection
        class_methods = [method for method in result.methods if method.is_class_method]
        assert len(class_methods) == 1
        assert class_methods[0].selector == "new"

        # Test instance methods
        instance_methods = [
            method for method in result.methods if not method.is_class_method
        ]
        assert len(instance_methods) == 4

    def test_method_with_nested_blocks(self):
        """Test parsing method with nested Smalltalk blocks."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> complexBlock [
    ^ [ [ 1 + 2 ] value ] value
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "[ [ 1 + 2 ] value ] value" in method.body

    def test_method_with_string_containing_brackets(self):
        """Test parsing method with string containing brackets."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> stringWithBrackets [
    ^ 'string with ] bracket'
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "'string with ] bracket'" in method.body

    def test_method_with_comment_containing_brackets(self):
        """Test parsing method with comment containing brackets."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> commentWithBrackets [
    "comment with ] bracket"
    ^ self
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert '"comment with ] bracket"' in method.body

    def test_method_with_character_literal(self):
        """Test parsing method with character literal containing bracket."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> charLiteral [
    ^ $]
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "$]" in method.body

    def test_multiple_keyword_selector(self):
        """Test parsing method with multiple keyword selector."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> from: start to: end do: aBlock [
    start to: end do: aBlock
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.selector == "from:to:do:"

    def test_primitive_method(self):
        """Test parsing method with primitive call."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> primitiveExample [
    <primitive: 1>
    ^ self primitiveFailed
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "<primitive: 1>" in method.body

    def test_method_with_temporaries(self):
        """Test parsing method with temporary variables."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> withTemps [
    | temp1 temp2 temp3 |
    temp1 := 1.
    temp2 := 2.
    temp3 := temp1 + temp2.
    ^ temp3
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "| temp1 temp2 temp3 |" in method.body

    def test_cascading_messages(self):
        """Test parsing method with cascading messages."""
        tonel_content = """Class {
    #name : #TestClass
}

TestClass >> cascadeExample [
    self
        message1;
        message2;
        message3.
    ^ self
]"""

        result = self.parser.parse(tonel_content)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert "message1;" in method.body
        assert "message2;" in method.body
        assert "message3" in method.body


if __name__ == "__main__":
    pytest.main([__file__])
