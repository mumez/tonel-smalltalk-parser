"""Strict bracket boundary detection for Tonel method bodies.

Implements the bracket counting + lexical analysis approach from the BNF specification.
"""

import re


class BracketParser:
    """Handles precise method body boundary detection using bracket counting.

    While respecting string literals, comments, and character literals.
    """

    def __init__(self):
        # Character literal pattern: $x where x is any character
        self.char_literal_pattern = re.compile(r"\$.")

    def find_method_body_end(self, content: str, start_pos: int) -> int:
        """Find the end position of a method body starting from `[` at start_pos.

        Args:
            content: The content string
            start_pos: Position of the opening `[`

        Returns:
            Position of the matching closing `]`

        Raises:
            ValueError: If no matching bracket is found

        """
        if start_pos >= len(content) or content[start_pos] != "[":
            raise ValueError("start_pos must point to an opening bracket '['")

        pos = start_pos + 1  # Start after the opening '['
        bracket_count = 1

        while pos < len(content) and bracket_count > 0:
            char = content[pos]

            # Handle string literals
            if char == "'":
                pos = self._skip_string_literal(content, pos)
                continue

            # Handle comments
            elif char == '"':
                pos = self._skip_comment(content, pos)
                continue

            # Handle character literals
            elif char == "$":
                if pos + 1 < len(content):
                    pos += 2  # Skip $x
                else:
                    pos += 1
                continue

            # Handle brackets
            elif char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1

            pos += 1

        if bracket_count > 0:
            raise ValueError("Unmatched opening bracket - no closing ']' found")

        return pos - 1  # Return position of the closing ']'

    def _skip_string_literal(self, content: str, start_pos: int) -> int:
        """Skip over a string literal starting at start_pos.

        Handles escaped quotes ('').

        Args:
            content: The content string
            start_pos: Position of the opening quote

        Returns:
            Position after the closing quote

        """
        if content[start_pos] != "'":
            return start_pos

        pos = start_pos + 1

        while pos < len(content):
            if content[pos] == "'":
                # Check for escaped quote
                if pos + 1 < len(content) and content[pos + 1] == "'":
                    pos += 2  # Skip ''
                else:
                    return pos + 1  # Skip closing quote
            else:
                pos += 1

        # Unclosed string literal - return end of content
        return len(content)

    def _skip_comment(self, content: str, start_pos: int) -> int:
        """Skip over a comment starting at start_pos.

        Handles escaped quotes ("").

        Args:
            content: The content string
            start_pos: Position of the opening quote

        Returns:
            Position after the closing quote

        """
        if content[start_pos] != '"':
            return start_pos

        pos = start_pos + 1

        while pos < len(content):
            if content[pos] == '"':
                # Check for escaped quote
                if pos + 1 < len(content) and content[pos + 1] == '"':
                    pos += 2  # Skip ""
                else:
                    return pos + 1  # Skip closing quote
            else:
                pos += 1

        # Unclosed comment - return end of content
        return len(content)

    def extract_method_body(self, content: str, start_pos: int) -> tuple[str, int]:
        """Extract method body content starting from `[` at start_pos.

        Args:
            content: The content string
            start_pos: Position of the opening `[`

        Returns:
            Tuple of (method_body_content, end_position)

        """
        end_pos = self.find_method_body_end(content, start_pos)
        body_content = content[start_pos + 1 : end_pos]  # Exclude the brackets
        return body_content, end_pos

    def find_method_boundaries(self, content: str) -> list:
        """Find all method boundaries in the content.

        Args:
            content: The content string

        Returns:
            List of tuples (start_pos, end_pos) for each method body

        """
        boundaries = []
        pos = 0

        while pos < len(content):
            # Find next potential method start
            bracket_pos = content.find("[", pos)
            if bracket_pos == -1:
                break

            try:
                end_pos = self.find_method_body_end(content, bracket_pos)
                boundaries.append((bracket_pos, end_pos))
                pos = end_pos + 1
            except ValueError:
                # Skip this bracket and continue
                pos = bracket_pos + 1

        return boundaries


def test_bracket_parser():
    """Test the bracket parser with various edge cases."""
    parser = BracketParser()

    # Test 1: Simple method
    content1 = "Counter >> value [\n    ^ value\n]"
    start = content1.find("[")
    body, end = parser.extract_method_body(content1, start)
    print(f"Test 1: {body!r}")

    # Test 2: Nested blocks
    content2 = "TestClass >> complexBlock [\n    ^ [ [ 1 + 2 ] value ] value\n]"
    start = content2.find("[")
    body, end = parser.extract_method_body(content2, start)
    print(f"Test 2: {body!r}")

    # Test 3: String with bracket
    content3 = "TestClass >> stringWithBrackets [\n    ^ 'string with ] bracket'\n]"
    start = content3.find("[")
    body, end = parser.extract_method_body(content3, start)
    print(f"Test 3: {body!r}")

    # Test 4: Comment with bracket
    content4 = (
        "TestClass >> commentWithBrackets [\n    "
        '"comment with ] bracket"\n    ^ self\n]'
    )
    start = content4.find("[")
    body, end = parser.extract_method_body(content4, start)
    print(f"Test 4: {body!r}")

    # Test 5: Character literal
    content5 = "TestClass >> charLiteral [\n    ^ $]\n]"
    start = content5.find("[")
    body, end = parser.extract_method_body(content5, start)
    print(f"Test 5: {body!r}")


if __name__ == "__main__":
    test_bracket_parser()
