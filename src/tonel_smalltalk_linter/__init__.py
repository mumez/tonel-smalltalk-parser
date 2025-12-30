"""Tonel Smalltalk Linter package.

A linter for Tonel Smalltalk files that checks for best practices
and code quality issues.
"""

from .linter import LintIssue, TonelLinter

__version__ = "0.1.0"
__all__ = ["LintIssue", "TonelLinter"]
