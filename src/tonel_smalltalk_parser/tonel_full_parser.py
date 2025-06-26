"""Tonel full parser implementation.

Combined parser that handles both Tonel format parsing and Smalltalk method
body validation.
"""

from .base_parser import BaseParser
from .smalltalk_parser import SmalltalkParser
from .tonel_parser import TonelFile, TonelParser


class TonelFullParser(BaseParser):
    """Full Tonel parser that validates both Tonel and Smalltalk syntax.

    This parser combines TonelParser and SmalltalkParser to provide complete
    validation of Tonel files including Smalltalk method body syntax.
    """

    def __init__(self):
        """Initialize the full parser with both Tonel and Smalltalk parsers."""
        self.tonel_parser = TonelParser()
        self.smalltalk_parser = SmalltalkParser()

    def parse(self, content: str) -> TonelFile:
        """Parse Tonel content and return structured representation.

        Args:
            content: The Tonel content as a string

        Returns:
            TonelFile: The parsed Tonel file structure

        Raises:
            ValueError: If the Tonel structure is invalid
            SyntaxError: If any method body contains syntax errors

        """
        # Parse Tonel structure
        tonel_file = self.tonel_parser.parse(content)

        # Validate each method body with Smalltalk parser
        for method in tonel_file.methods:
            try:
                self.smalltalk_parser.parse(method.body)
            except (SyntaxError, Exception) as e:
                raise SyntaxError(
                    f"Invalid Smalltalk syntax in method "
                    f"{method.class_name}>>{method.selector}: {e}"
                ) from e

        return tonel_file
