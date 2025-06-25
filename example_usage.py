#!/usr/bin/env python3
"""Example demonstrating how to use the Tonel and Smalltalk parsers."""

from src.tonel_smalltalk_parser import (
    Assignment,
    Block,
    MessageSend,
    Return,
    TonelParser,
    parse_smalltalk_method_body,
)


def main():
    # Example 1: Parse a complete Tonel file
    print("=== Example 1: Complete Tonel File Parsing ===")

    tonel_content = """
"A simple counter class for demonstration"
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
Counter >> increment [
    value := value + 1.
    ^ self
]
"""

    parser = TonelParser()
    tonel_file = parser.parse(tonel_content)

    print(f"Class type: {tonel_file.class_definition.type}")
    print(f"Class name: {tonel_file.class_definition.metadata.get('name', 'Unknown')}")
    print(f"Number of methods: {len(tonel_file.methods)}")
    print(
        f"Comment: {tonel_file.comment[:50]}..." if tonel_file.comment else "No comment"
    )

    print("\nMethods:")
    for method in tonel_file.methods:
        print(f"  - {method.class_name} >> {method.selector}")
        if method.metadata:
            category = method.metadata.get("category", "uncategorized")
            print(f"    Category: {category}")

    # Example 2: Parse individual Smalltalk method bodies
    print("\n=== Example 2: Smalltalk Method Body Parsing ===")

    method_examples = [
        "^ value",
        "value := anObject",
        "| temp | temp := self getValue. ^ temp + 42",
        "[ :x | x + 1 ] value: 5",
        "stream nextPut: 'Hello'; nextPut: ' '; nextPut: 'World'",
        "collection do: [ :each | each printString ]",
    ]

    for i, method_body in enumerate(method_examples, 1):
        print(f"\nExample {i}: {method_body}")
        try:
            ast = parse_smalltalk_method_body(method_body)
            print("  Parsed successfully!")
            temps = ast.temporaries.variables if ast.temporaries else "None"
            print(f"  Temporaries: {temps}")
            print(f"  Statements: {len(ast.statements)}")

            # Analyze first statement
            if ast.statements:
                stmt = ast.statements[0]
                if isinstance(stmt, Return):
                    print("  First statement: Return")
                elif isinstance(stmt, Assignment):
                    print(f"  First statement: Assignment to '{stmt.variable}'")
                elif isinstance(stmt, MessageSend):
                    print(f"  First statement: Message '{stmt.selector}' to receiver")
                elif isinstance(stmt, Block):
                    param_count = len(stmt.parameters)
                    print(f"  First statement: Block with {param_count} parameters")
                else:
                    print(f"  First statement: {type(stmt).__name__}")

        except Exception as e:
            print(f"  Parse error: {e}")

    # Example 3: Integration - Parse Tonel and then parse method bodies
    print("\n=== Example 3: Full Integration ===")

    for method in tonel_file.methods:
        print(f"\nAnalyzing method: {method.selector}")
        try:
            ast = parse_smalltalk_method_body(method.body)
            print("  Method body parsed successfully")
            print(f"  Has temporaries: {'Yes' if ast.temporaries else 'No'}")
            print(f"  Statement count: {len(ast.statements)}")

            # Check if method returns something
            has_return = any(isinstance(stmt, Return) for stmt in ast.statements)
            print(f"  Has explicit return: {'Yes' if has_return else 'No'}")

        except Exception as e:
            print(f"  Parse error: {e}")


if __name__ == "__main__":
    main()
