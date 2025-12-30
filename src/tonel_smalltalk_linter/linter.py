"""Tonel Smalltalk Linter.

Lint Tonel files for Smalltalk best practices and code quality issues.
Uses TonelFullParser for accurate parsing and analysis.
"""

from pathlib import Path
import re

from tonel_smalltalk_parser.tonel_full_parser import TonelFullParser
from tonel_smalltalk_parser.tonel_parser import MethodDefinition, TonelFile


class LintIssue:
    """Represents a linting issue."""

    def __init__(self, severity: str, message: str, line_number: int | None = None):
        self.severity = severity  # 'warning' or 'error'
        self.message = message
        self.line_number = line_number


class TonelLinter:
    """Simple linter for Tonel Smalltalk files."""

    def __init__(self):
        self.parser = TonelFullParser()
        self.warnings = 0
        self.errors = 0

    def lint_file(self, file_path: Path) -> list[LintIssue]:
        """Lint a single Tonel file and return list of issues."""
        issues = []

        try:
            # Parse the file
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tonel_file = self.parser.parse(content)

            # Run lint checks
            issues.extend(self._check_class_prefix(tonel_file))
            issues.extend(self._check_instance_variables(tonel_file))
            issues.extend(self._check_methods(tonel_file))

        except Exception as e:
            issues.append(LintIssue("error", f"Failed to parse file: {e}"))

        return issues

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
                    f"No class prefix: {class_name} (consider adding project prefix)",
                )
            )

        return issues

    def _check_instance_variables(self, tonel_file: TonelFile) -> list[LintIssue]:
        """Check instance variable count."""
        issues = []

        inst_vars = tonel_file.class_definition.metadata.get("instVars", [])
        if len(inst_vars) > 10:
            issues.append(
                LintIssue(
                    "warning",
                    (
                        f"Too many instance variables: {len(inst_vars)} "
                        "(consider splitting responsibilities)"
                    ),
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
                        (
                            f"Method '{method.selector}' too long: "
                            f"{body_lines} lines (limit: {limit})"
                        ),
                    )
                )
            else:
                issues.append(
                    LintIssue(
                        "warning",
                        (
                            f"Method '{method.selector}' long: "
                            f"{body_lines} lines (recommended: {limit})"
                        ),
                    )
                )

        return issues

    def _check_direct_access(
        self, method: MethodDefinition, inst_vars: set
    ) -> list[LintIssue]:
        """Check for direct instance variable access."""
        issues = []

        # Skip accessor and initialization methods
        category = method.metadata.get("category", "") if method.metadata else ""
        if any(
            keyword in category.lower() for keyword in ["accessing", "initialization"]
        ):
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
                            (
                                f"Direct access to '{var}' in "
                                f"'{method.selector}' (use self {var})"
                            ),
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
            if issue.severity == "error":
                print(f"  ❌ {issue.message}")
                self.errors += 1
            else:
                print(f"  ⚠️  {issue.message}")
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
