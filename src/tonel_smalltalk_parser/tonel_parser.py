"""Tonel parser implementation.
Manual parser that handles Tonel format parsing with precise bracket matching.
"""

from dataclasses import dataclass
import re
from typing import Any

from .bracket_parser import BracketParser


@dataclass
class MethodDefinition:
    """Represents a method definition in Tonel format."""

    class_name: str
    is_class_method: bool
    selector: str
    body: str
    metadata: dict[str, Any] | None = None


@dataclass
class ClassDefinition:
    """Represents a class definition in Tonel format."""

    type: str  # "Class", "Trait", or "Extension"
    metadata: dict[str, Any]


@dataclass
class TonelFile:
    """Represents a complete Tonel file."""

    comment: str | None
    class_definition: ClassDefinition
    methods: list[MethodDefinition]


class TonelParser:
    """Manual Tonel parser that handles Tonel format parsing."""

    def __init__(self):
        # Patterns for parsing
        self.comment_pattern = re.compile(r'^"([^"]*)"', re.MULTILINE | re.DOTALL)
        self.class_def_pattern = re.compile(
            r"(Class|Trait|Extension)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL
        )

        # Method header pattern (without body)
        self.method_header_pattern = re.compile(
            r"(?:(\{[^}]*\})\s*)?"  # optional metadata
            + r"([A-Z][a-zA-Z0-9_]*)\s*"  # class name
            + r"(?:(class)\s*)?"  # optional "class"
            + r">>\s*"  # >>
            + r"((?:[a-zA-Z][a-zA-Z0-9_]*\s*:\s*[a-zA-Z0-9_]*\s*)*[a-zA-Z][a-zA-Z0-9_]*(?:\s*:\s*[a-zA-Z0-9_]*)?|[+\-*\/=><@%~|&?,]\s*[a-zA-Z0-9_]*)\s*"  # selector with args
            + r"\[",  # opening bracket
            re.MULTILINE | re.DOTALL,
        )

        # Initialize bracket parser for precise method body extraction
        self.bracket_parser = BracketParser()

    def parse(self, content: str) -> TonelFile:
        """Parse Tonel content and return structured representation."""
        content = content.strip()

        # Extract comment
        comment = None
        comment_match = self.comment_pattern.match(content)
        if comment_match:
            comment = comment_match.group(1)
            content = content[comment_match.end() :].strip()

        # Extract class definition
        class_def_match = self.class_def_pattern.search(content)
        if not class_def_match:
            raise ValueError("No valid class definition found")

        class_type = class_def_match.group(1)
        class_metadata_str = class_def_match.group(2)
        class_metadata = self._parse_simple_ston(class_metadata_str)

        class_definition = ClassDefinition(type=class_type, metadata=class_metadata)

        # Remove class definition from content
        content = content[class_def_match.end() :].strip()

        # Extract methods using precise bracket parsing
        methods = []
        for match in self.method_header_pattern.finditer(content):
            metadata_str = match.group(1)
            class_name = match.group(2)
            is_class_method = match.group(3) == "class"
            selector_raw = match.group(4).strip()

            # Clean up selector - extract just the keywords/operators
            selector = self._extract_selector(selector_raw)

            # Find the opening bracket position
            bracket_pos = match.end() - 1  # Position of '['

            try:
                # Extract method body using precise bracket parsing
                body, end_pos = self.bracket_parser.extract_method_body(
                    content, bracket_pos
                )

                metadata = None
                if metadata_str:
                    metadata = self._parse_simple_ston(metadata_str[1:-1])  # Remove { }

                method = MethodDefinition(
                    class_name=class_name,
                    is_class_method=is_class_method,
                    selector=selector,
                    body=body,
                    metadata=metadata,
                )
                methods.append(method)

            except ValueError as e:
                # Skip methods with bracket parsing errors
                print(f"Warning: Failed to parse method {class_name}>>{selector}: {e}")
                continue

        return TonelFile(
            comment=comment, class_definition=class_definition, methods=methods
        )

    def _extract_selector(self, selector_raw: str) -> str:
        """Extract clean selector from raw selector string."""
        import re

        # Handle binary selectors - look for operator at start
        binary_match = re.match(r"^([+\-*\/=><@%~|&?,])", selector_raw)
        if binary_match:
            return binary_match.group(1)

        # Handle keyword selectors: extract all keywords (word:)
        keywords = re.findall(r"[a-zA-Z][a-zA-Z0-9_]*:", selector_raw)
        if keywords:
            return "".join(keywords)

        # Handle unary selectors (single word)
        word_match = re.match(r"^([a-zA-Z][a-zA-Z0-9_]*)", selector_raw)
        if word_match:
            return word_match.group(1)

        # Fallback
        return selector_raw.strip()

    def _parse_simple_ston(self, ston_str: str) -> dict[str, Any]:
        """Parse simple STON format (very basic implementation)."""
        if not ston_str.strip():
            return {}

        result = {}

        # Simple key-value pattern matching
        # This is a simplified implementation that handles basic cases
        pattern = re.compile(r"#([a-zA-Z][a-zA-Z0-9_]*)\s*:\s*([^,}]+)", re.MULTILINE)

        for match in pattern.finditer(ston_str):
            key = match.group(1)
            value_str = match.group(2).strip()

            # Parse value
            if value_str.startswith("#"):
                # Symbol
                result[key] = value_str[1:]
            elif value_str.startswith("'") and value_str.endswith("'"):
                # String
                result[key] = value_str[1:-1]
            elif value_str.startswith("[") and value_str.endswith("]"):
                # Array (simplified)
                array_content = value_str[1:-1].strip()
                if array_content:
                    items = [
                        item.strip().strip("'") for item in array_content.split(",")
                    ]
                    result[key] = items
                else:
                    result[key] = []
            elif value_str.isdigit():
                # Number
                result[key] = int(value_str)
            elif value_str in ["true", "false"]:
                # Boolean
                result[key] = value_str == "true"
            elif value_str == "nil":
                # Nil
                result[key] = None
            else:
                # Default to string
                result[key] = value_str

        return result

    def parse_file(self, filepath: str) -> TonelFile:
        """Parse Tonel file and return structured representation."""
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        return self.parse(content)
