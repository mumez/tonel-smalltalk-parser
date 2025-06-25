"""A Python package for parsing Tonel and Smalltalk code."""

from .smalltalk_parser import (
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
    Variable,
    parse_smalltalk_method_body,
)
from .tonel_parser import ClassDefinition, MethodDefinition, TonelFile, TonelParser

# TonelParser is now the main parser class

__all__ = [
    "Assignment",
    "Block",
    "Cascade",
    "ClassDefinition",
    "DynamicArray",
    "Literal",
    "LiteralArray",
    "MessageSend",
    "MethodDefinition",
    "Return",
    "SmalltalkLexer",
    "SmalltalkParser",
    "SmalltalkSequence",
    "TemporaryVariables",
    "TonelFile",
    "TonelParser",
    "Variable",
    "parse_smalltalk_method_body",
]
