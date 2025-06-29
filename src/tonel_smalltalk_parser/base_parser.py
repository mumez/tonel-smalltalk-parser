"""Base parser implementation with common functionality."""

from abc import ABC, abstractmethod
from typing import Any, TypeAlias, TypeVar

T = TypeVar("T")
ValidationResult: TypeAlias = tuple[bool, dict[str, Any] | None]


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

    def validate(self, content: str) -> ValidationResult:
        """Validate if the content can be parsed.

        Args:
            content: The content as a string

        Returns:
            ValidationResult containing:
            - bool: True if content can be parsed successfully, False otherwise
            - Optional[Dict]: Error information if parsing failed, None if successful.
              Contains 'reason' (str), 'line' (int), 'error_text' (str)

        """
        try:
            self.parse(content)
            return True, None
        except (ValueError, SyntaxError) as e:
            error_info = self._extract_error_info(content, e)
            return False, error_info
        except Exception as e:
            error_info = {
                "reason": f"Unexpected error: {type(e).__name__}",
                "line": 1,
                "error_text": str(e),
            }
            return False, error_info

    def _extract_error_info(self, content: str, exception: Exception) -> dict[str, Any]:
        """Extract error information from parsing exception.

        Args:
            content: The original content being parsed
            exception: The exception that occurred during parsing

        Returns:
            Dict containing error information with keys:
            - reason: Error reason/type
            - line: Line number where error occurred
            - error_text: Text around the error location

        """
        lines = content.split("\n")
        error_msg = str(exception)

        # Try to extract line number from exception message
        line_num = 1
        if hasattr(exception, "lineno") and getattr(exception, "lineno", None):
            line_num = exception.lineno
        else:
            # Try to parse line number from error message
            import re

            line_match = re.search(r"line (\d+)", error_msg, re.IGNORECASE)
            if line_match:
                line_num = int(line_match.group(1))

        # Get error text (line where error occurred)
        error_text = ""
        if 1 <= line_num <= len(lines):
            error_text = lines[line_num - 1].strip()

        return {
            "reason": error_msg,
            "line": line_num,
            "error_text": error_text,
        }

    def validate_from_file(self, filepath: str) -> ValidationResult:
        """Validate if the file can be parsed.

        Args:
            filepath: Path to the file

        Returns:
            ValidationResult containing:
            - bool: True if file can be parsed successfully, False otherwise
            - Optional[Dict]: Error information if parsing failed, None if successful.
              Contains 'reason' (str), 'line' (int), 'error_text' (str)

        """
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            return self.validate(content)
        except OSError as e:
            error_info = {
                "reason": f"Failed to read file: {e}",
                "line": 1,
                "error_text": filepath,
            }
            return False, error_info
        except Exception as e:
            error_info = {
                "reason": f"Unexpected error reading file: {type(e).__name__}",
                "line": 1,
                "error_text": str(e),
            }
            return False, error_info

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
