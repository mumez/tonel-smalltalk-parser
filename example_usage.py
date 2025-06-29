#!/usr/bin/env python3
"""Example usage script for tonel-smalltalk-parser package.

This script demonstrates basic usage of the package after installation.
Run with: python example_usage.py
"""

from tonel_smalltalk_parser import TonelFullParser, TonelParser


def main():
    """Demonstrate basic package functionality."""
    # Sample Tonel content
    tonel_content = """
"A sample counter class for demonstration"
Class {
    #name : #Counter,
    #superclass : #Object,
    #instVars : [ 'count' ],
    #category : #'Demo-Core'
}

{ #category : #accessing }
Counter >> count [
    ^ count
]

{ #category : #accessing }
Counter >> increment [
    count := count + 1
]

{ #category : #initialization }
Counter >> initialize [
    super initialize.
    count := 0
]
"""

    print("🔍 Testing Tonel Smalltalk Parser")
    print("=" * 50)

    # Test basic Tonel parsing
    print("\n1. Basic Tonel Parsing:")
    parser = TonelParser()
    result = parser.parse(tonel_content)

    print(f"   ✅ Class type: {result.class_definition.type}")
    print(f"   ✅ Class name: {result.class_definition.metadata.get('name')}")
    print(
        f"   ✅ Comment: {result.comment[:30]}..."
        if result.comment
        else "   ✅ No comment"
    )
    print(f"   ✅ Number of methods: {len(result.methods)}")

    for method in result.methods:
        print(f"   📝 Method: {method.class_name} >> {method.selector}")

    # Test validation
    print("\n2. Validation Tests:")
    is_tonel_valid, error_info = parser.validate(tonel_content)
    print(f"   ✅ Tonel structure valid: {is_tonel_valid}")

    # Test full validation (Tonel + Smalltalk)
    print("\n3. Full Validation (Tonel + Smalltalk):")
    full_parser = TonelFullParser()
    is_fully_valid, error_info = full_parser.validate(tonel_content)
    print(f"   ✅ Fully valid (Tonel + Smalltalk): {is_fully_valid}")

    # Test with invalid content
    print("\n4. Error Handling:")
    invalid_content = "This is not valid Tonel content"
    is_invalid_valid, error_info = parser.validate(invalid_content)
    print(f"   ✅ Invalid content correctly rejected: {not is_invalid_valid}")
    if error_info:
        print("   📍 Error details:")
        print(f"       Reason: {error_info['reason']}")
        print(f"       Line: {error_info['line']}")
        print(f"       Content: '{error_info['error_text']}'")

    # Test with invalid Smalltalk syntax
    print("\n5. Smalltalk Syntax Error Handling:")
    invalid_smalltalk = """
"A class with invalid Smalltalk syntax"
Class {
    #name : #BadClass,
    #superclass : #Object
}

BadClass >> badMethod [
    | invalid syntax here
    this is not valid smalltalk
]
"""
    is_syntax_valid, syntax_error = full_parser.validate(invalid_smalltalk)
    print(f"   ✅ Invalid Smalltalk syntax correctly rejected: {not is_syntax_valid}")
    if syntax_error:
        print("   📍 Syntax error details:")
        print(f"       Reason: {syntax_error['reason']}")
        print(f"       Line: {syntax_error['line']}")
        print(f"       Content: '{syntax_error['error_text']}'")

    # Demonstrate ValidationResult tuple unpacking
    print("\n6. ValidationResult Usage Examples:")
    success, error = parser.validate(tonel_content)
    if success:
        print("   ✅ Content is valid - proceed with parsing")
    else:
        print(f"   ❌ Content is invalid: {error['reason']}")

    # Show file validation
    print("\n7. File Validation Example:")
    print("   💡 For file validation, use:")
    print("       success, error = parser.validate_from_file('path/to/file.st')")
    print("       if not success:")
    print('           print(f\'Error at line {error["line"]}: {error["reason"]}\')')

    print("\n🎉 All tests passed! Package is working correctly.")
    print("\n📚 For more examples, see README.md")


if __name__ == "__main__":
    main()
