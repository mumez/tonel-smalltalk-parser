"""Tests for CLI functionality."""

from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest

from tonel_smalltalk_parser.cli import main, validate_tonel_file


class TestValidateTonelFile:
    """Test the validate_tonel_file function."""

    def test_validate_valid_tonel_file(self):
        """Test validation of a valid Tonel file."""
        content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> value [
    ^ value
]"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            result = validate_tonel_file(f.name, without_method_body=False)
            assert result is True

            Path(f.name).unlink()

    def test_validate_valid_tonel_file_without_method_body(self):
        """Test validation of Tonel structure only."""
        content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> value [
    ^ ( unclosed parenthesis
]"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            # Should pass when only validating structure
            result = validate_tonel_file(f.name, without_method_body=True)
            assert result is True

            # Should fail when validating method bodies
            result = validate_tonel_file(f.name, without_method_body=False)
            assert result is False

            Path(f.name).unlink()

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        result = validate_tonel_file("nonexistent.st")
        assert result is False

    def test_validate_directory(self):
        """Test validation of directory instead of file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_tonel_file(tmpdir)
            assert result is False

    def test_validate_invalid_tonel_file(self):
        """Test validation of invalid Tonel file."""
        content = "Invalid Tonel content"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            result = validate_tonel_file(f.name, without_method_body=False)
            assert result is False

            result = validate_tonel_file(f.name, without_method_body=True)
            assert result is False

            Path(f.name).unlink()


class TestCLIMain:
    """Test the CLI main function."""

    def test_cli_with_valid_file(self):
        """Test CLI with valid Tonel file."""
        content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> value [
    ^ value
]"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            with patch("sys.argv", ["validate-tonel", f.name]):
                result = main()
                assert result == 0

            Path(f.name).unlink()

    def test_cli_with_invalid_file(self):
        """Test CLI with invalid Tonel file."""
        content = "Invalid Tonel content"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            with patch("sys.argv", ["validate-tonel", f.name]):
                result = main()
                assert result == 1

            Path(f.name).unlink()

    def test_cli_with_without_method_body_flag(self):
        """Test CLI with --without-method-body flag."""
        content = """Class {
    #name : #Counter,
    #superclass : #Object,
    #category : #'Demo-Core'
}

Counter >> value [
    ^ ( unclosed parenthesis
]"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            # Should pass with --without-method-body
            with patch("sys.argv", ["validate-tonel", "--without-method-body", f.name]):
                result = main()
                assert result == 0

            # Should fail without the flag
            with patch("sys.argv", ["validate-tonel", f.name]):
                result = main()
                assert result == 1

            Path(f.name).unlink()

    def test_cli_with_nonexistent_file(self):
        """Test CLI with non-existent file."""
        with patch("sys.argv", ["validate-tonel", "nonexistent.st"]):
            result = main()
            assert result == 1

    def test_cli_version(self):
        """Test CLI version flag."""
        with patch("sys.argv", ["validate-tonel", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_help(self):
        """Test CLI help flag."""
        with patch("sys.argv", ["validate-tonel", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
