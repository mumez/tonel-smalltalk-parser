"""Base parser implementation with common functionality."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    @abstractmethod
    def parse(self, content: str) -> Any:
        """Parse content and return structured representation.

        Args:
            content: The content as a string

        Returns:
            The parsed structure

        Raises:
            ValueError: If the content structure is invalid
            SyntaxError: If the content contains syntax errors

        """
        pass

    def validate(self, content: str) -> bool:
        """Validate if the content can be parsed.

        Args:
            content: The content as a string

        Returns:
            bool: True if content can be parsed successfully, False otherwise

        """
        try:
            self.parse(content)
            return True
        except (ValueError, SyntaxError, Exception):
            return False

    def validate_from_file(self, filepath: str) -> bool:
        """Validate if the file can be parsed.

        Args:
            filepath: Path to the file

        Returns:
            bool: True if file can be parsed successfully, False otherwise

        """
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            return self.validate(content)
        except (OSError, Exception):
            return False

    def parse_from_file(self, filepath: str) -> Any:
        """Parse file and return structured representation.

        Args:
            filepath: Path to the file

        Returns:
            The parsed structure

        Raises:
            ValueError: If the file structure is invalid
            SyntaxError: If the file contains syntax errors
            OSError: If the file cannot be read

        """
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        return self.parse(content)
