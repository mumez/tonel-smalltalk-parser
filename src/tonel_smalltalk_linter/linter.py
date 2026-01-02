"""Tonel Smalltalk Linter.

Lint Tonel files for Smalltalk best practices and code quality issues.
Uses TonelFullParser for accurate parsing and analysis.
"""

from pathlib import Path
import re

from tonel_smalltalk_parser.tonel_full_parser import TonelFullParser
from tonel_smalltalk_parser.tonel_parser import MethodDefinition, TonelFile


class LintIssue:
    """Represents a linting issue.

    Attributes:
        severity: 'warning' or 'error'
        message: Description of the issue
        class_name: Name of the class where issue was found (optional)
        selector: Method selector where issue was found (optional)
        is_class_method: True if issue is in a class method (optional)

    """

    def __init__(
        self,
        severity: str,
        message: str,
        class_name: str | None = None,
        selector: str | None = None,
        is_class_method: bool | None = None,
    ):
        self.severity = severity
        self.message = message
        self.class_name = class_name
        self.selector = selector
        self.is_class_method = is_class_method


class TonelLinter:
    """Simple linter for Tonel Smalltalk files."""

    def __init__(self):
        self.parser = TonelFullParser()
        self.warnings = 0
        self.errors = 0

    def lint(self, content: str) -> list[LintIssue]:
        """Lint Tonel content and return list of issues.

        Args:
            content: The Tonel file content as a string

        Returns:
            list[LintIssue]: List of linting issues found

        """
        issues = []

        try:
            tonel_file = self.parser.parse(content)

            # Run lint checks
            issues.extend(self._check_class_prefix(tonel_file))
            issues.extend(self._check_instance_variables(tonel_file))
            issues.extend(self._check_methods(tonel_file))

        except Exception as e:
            issues.append(LintIssue("error", f"Failed to parse content: {e}"))

        return issues

    def lint_from_file(self, file_path: Path) -> list[LintIssue]:
        """Lint a Tonel file and return list of issues.

        Args:
            file_path: Path to the Tonel file

        Returns:
            list[LintIssue]: List of linting issues found

        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return self.lint(content)
        except Exception as e:
            return [LintIssue("error", f"Failed to read file: {e}")]

    def _check_class_prefix(self, tonel_file: TonelFile) -> list[LintIssue]:
        """Check if class has appropriate prefix."""
        issues = []

        class_name = tonel_file.class_definition.metadata.get("name", "").strip("#")
        if not class_name:
            return issues

        # Skip BaselineOf and Test classes
        if class_name.startswith("BaselineOf") or class_name.endswith("Test"):
            return issues

        # Check for 2+ character prefix (e.g., ST, Zn, MC)
        # Valid patterns:
        # - Two or more consecutive uppercase: STClass, MCPackage
        # - Uppercase + lowercase then immediately another uppercase: ZnServer, RbNode
        # - Must have at least 3 chars and match one of these patterns
        has_prefix = len(class_name) >= 3 and (
            re.match(r"^[A-Z]{2,}", class_name)
            or re.match(r"^[A-Z][a-z][A-Z]", class_name)
        )

        if not has_prefix:
            issues.append(
                LintIssue(
                    "warning",
                    "No class prefix (consider adding project prefix)",
                    class_name=class_name,
                )
            )

        return issues

    def _check_instance_variables(self, tonel_file: TonelFile) -> list[LintIssue]:
        """Check instance variable count."""
        issues = []

        class_name = tonel_file.class_definition.metadata.get("name", "").strip("#")
        inst_vars = tonel_file.class_definition.metadata.get("instVars", [])
        if len(inst_vars) > 10:
            issues.append(
                LintIssue(
                    "warning",
                    (
                        f"Too many instance variables: {len(inst_vars)} "
                        "(consider splitting responsibilities)"
                    ),
                    class_name=class_name,
                )
            )

        return issues

    def _check_methods(self, tonel_file: TonelFile) -> list[LintIssue]:
        """Check method lengths and direct variable access."""
        issues = []

        # Get instance variables for direct access check
        inst_vars = set()
        for var in tonel_file.class_definition.metadata.get("instVars", []):
            var_name = var.strip("'\"")
            if var_name:
                inst_vars.add(var_name)

        for method in tonel_file.methods:
            issues.extend(self._check_method_length(method))
            issues.extend(self._check_direct_access(method, inst_vars))

        return issues

    def _check_method_length(self, method: MethodDefinition) -> list[LintIssue]:
        """Check if method is too long."""
        issues = []

        # Count lines in method body
        body_lines = len(method.body.strip().split("\n"))

        # Determine limit based on category (simplified check)
        category = method.metadata.get("category", "") if method.metadata else ""
        is_special_category = any(
            keyword in category.lower()
            for keyword in ["building", "initialization", "testing", "data", "examples"]
        )

        limit = 40 if is_special_category else 15

        if body_lines > limit:
            if body_lines > 24 and limit == 15:
                issues.append(
                    LintIssue(
                        "error",
                        f"Method too long: {body_lines} lines (limit: {limit})",
                        class_name=method.class_name,
                        selector=method.selector,
                        is_class_method=method.is_class_method,
                    )
                )
            else:
                issues.append(
                    LintIssue(
                        "warning",
                        f"Method long: {body_lines} lines (recommended: {limit})",
                        class_name=method.class_name,
                        selector=method.selector,
                        is_class_method=method.is_class_method,
                    )
                )

        return issues

    def _is_accessor_method(self, method: MethodDefinition) -> bool:
        """Check if method is an accessor method.

        Accessor methods are allowed to directly access instance variables.
        Patterns include: accessing, private-accessing, accessing-properties, etc.

        Args:
            method: The method to check

        Returns:
            bool: True if method is an accessor method

        """
        category = method.metadata.get("category", "") if method.metadata else ""
        category_lower = category.lower()

        # Any category containing 'accessing' is considered an accessor
        return "accessing" in category_lower

    def _is_initializer_method(self, method: MethodDefinition) -> bool:
        """Check if method is an initializer method.

        Initializer methods are allowed to directly access instance variables.
        Patterns include: initialization, initializing, initialize-release,
        class initialization, etc.

        Args:
            method: The method to check

        Returns:
            bool: True if method is an initializer method

        """
        category = method.metadata.get("category", "") if method.metadata else ""
        category_lower = category.lower()

        # Check for various initialization patterns
        initialization_patterns = [
            "initializ",  # Matches: initialization, initializing, initialize-release
            "class initialization",
        ]

        return any(pattern in category_lower for pattern in initialization_patterns)

    def _check_direct_access(
        self, method: MethodDefinition, inst_vars: set
    ) -> list[LintIssue]:
        """Check for direct instance variable access."""
        issues = []

        # Skip accessor and initialization methods
        if self._is_accessor_method(method) or self._is_initializer_method(method):
            return issues

        # Check method body for direct variable access
        body_lines = method.body.strip().split("\n")

        for line in body_lines:
            line = line.strip()
            if not line:
                continue

            for var in inst_vars:
                # Look for direct access patterns (simplified)
                # varName := value or ^ varName
                if (
                    re.search(rf"\b{re.escape(var)}\s*:=", line)
                    or re.search(rf"^\^\s*{re.escape(var)}\b", line)
                ) and "self" not in line.split(var)[0]:  # Rough check
                    issues.append(
                        LintIssue(
                            "warning",
                            f"Direct access to '{var}' (use self {var})",
                            class_name=method.class_name,
                            selector=method.selector,
                            is_class_method=method.is_class_method,
                        )
                    )
                    break

        return issues

    def print_issues(self, file_path: Path, issues: list[LintIssue]):
        """Print lint issues for a file."""
        if not issues:
            print(f"✓ {file_path.name}")
            return

        print(f"⚠ {file_path.name}")

        for issue in issues:
            # Build location string
            location = ""
            if issue.class_name:
                location = issue.class_name
                if issue.selector:
                    method_prefix = " class>>" if issue.is_class_method else ">>"
                    location += f"{method_prefix}{issue.selector}"
                location = f"[{location}] "

            message = f"{location}{issue.message}"

            if issue.severity == "error":
                print(f"  ❌ {message}")
                self.errors += 1
            else:
                print(f"  ⚠️  {message}")
                self.warnings += 1

        print()

    def print_summary(self, files_analyzed: int):
        """Print final summary."""
        print("─────────────────────────────────")
        print("Summary:")
        print(f"  Files analyzed: {files_analyzed}")
        print(f"  Warnings: {self.warnings}")
        print(f"  Errors: {self.errors}")

        if self.errors > 0:
            print("\n❌ Errors found - consider fixing before import")
            return 2
        elif self.warnings > 0:
            print("\n⚠️  Warnings found - review recommended")
            return 1
        else:
            print("\n✓ No issues found")
            return 0
