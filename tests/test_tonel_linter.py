"""Tests for Tonel Smalltalk Linter."""

from pathlib import Path
import tempfile

from tonel_smalltalk_linter import LintIssue, TonelLinter


class TestLintIssue:
    """Test LintIssue class."""

    def test_init(self):
        """Test LintIssue initialization."""
        issue = LintIssue("warning", "Test message", 10)
        assert issue.severity == "warning"
        assert issue.message == "Test message"
        assert issue.line_number == 10

    def test_init_without_line_number(self):
        """Test LintIssue initialization without line number."""
        issue = LintIssue("error", "Test message")
        assert issue.severity == "error"
        assert issue.message == "Test message"
        assert issue.line_number is None


class TestTonelLinter:
    """Test TonelLinter class."""

    def test_init(self):
        """Test TonelLinter initialization."""
        linter = TonelLinter()
        assert linter.warnings == 0
        assert linter.errors == 0
        assert hasattr(linter, "parser")

    def test_lint_from_file_with_valid_class(self):
        """Test linting a valid class file."""
        # Create a simple test file that should pass all checks
        content = """Class {
    #name : #STTestClass,
    #superclass : #Object,
    #instVars : [
        'var1'
    ],
    #category : #Test
}

{ #category : #accessing }
STTestClass >> var1 [
    ^ self var1
]

{ #category : #accessing }
STTestClass >> var1: aValue [
    var1 := aValue
]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False) as f:
            f.write(content)
            f.flush()

            try:
                linter = TonelLinter()
                issues = linter.lint_from_file(Path(f.name))

                # Should have no issues for a well-formed class
                # Note: accessor methods are allowed to access instance
                # variables directly
                assert len(issues) == 0
            finally:
                Path(f.name).unlink()

    def test_lint_with_valid_content(self):
        """Test linting valid Tonel content."""
        content = """Class {
    #name : #STTestClass,
    #superclass : #Object,
    #instVars : [
        'var1'
    ],
    #category : #Test
}

{ #category : #accessing }
STTestClass >> var1 [
    ^ self var1
]
"""

        linter = TonelLinter()
        issues = linter.lint(content)

        # Should have no issues for a well-formed class
        assert len(issues) == 0

    def test_check_class_prefix(self):
        """Test class prefix checking."""
        # Create a mock TonelFile
        from tonel_smalltalk_parser.tonel_parser import ClassDefinition, TonelFile

        # Single uppercase letter class name (no prefix)
        class_def = ClassDefinition(type="Class", metadata={"name": "#Object"})
        tonel_file = TonelFile(comment=None, class_definition=class_def, methods=[])

        linter = TonelLinter()
        issues = linter._check_class_prefix(tonel_file)

        # Should warn about missing prefix
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "No class prefix" in issues[0].message

    def test_check_class_prefix_with_good_prefix(self):
        """Test class prefix checking with good prefix."""
        from tonel_smalltalk_parser.tonel_parser import ClassDefinition, TonelFile

        class_def = ClassDefinition(type="Class", metadata={"name": "#STMyClass"})
        tonel_file = TonelFile(comment=None, class_definition=class_def, methods=[])

        linter = TonelLinter()
        issues = linter._check_class_prefix(tonel_file)

        # Should have no issues
        assert len(issues) == 0

    def test_check_class_prefix_with_lowercase_second_char(self):
        """Test class prefix with lowercase second character (e.g., Zn)."""
        from tonel_smalltalk_parser.tonel_parser import ClassDefinition, TonelFile

        class_def = ClassDefinition(type="Class", metadata={"name": "#ZnServer"})
        tonel_file = TonelFile(comment=None, class_definition=class_def, methods=[])

        linter = TonelLinter()
        issues = linter._check_class_prefix(tonel_file)

        # Should have no issues - Zn is a valid prefix
        assert len(issues) == 0

    def test_check_instance_variables(self):
        """Test instance variable count checking."""
        from tonel_smalltalk_parser.tonel_parser import ClassDefinition, TonelFile

        class_def = ClassDefinition(
            type="Class",
            metadata={
                "instVars": [
                    "var1",
                    "var2",
                    "var3",
                    "var4",
                    "var5",
                    "var6",
                    "var7",
                    "var8",
                    "var9",
                    "var10",
                    "var11",
                ]
            },
        )
        tonel_file = TonelFile(comment=None, class_definition=class_def, methods=[])

        linter = TonelLinter()
        issues = linter._check_instance_variables(tonel_file)

        # Should warn about too many instance variables
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "Too many instance variables" in issues[0].message

    def test_check_method_length(self):
        """Test method length checking."""
        from tonel_smalltalk_parser.tonel_parser import MethodDefinition

        # Create a long method (20 lines)
        long_body = "\n".join([f"    line{i} := {i}." for i in range(20)])
        method = MethodDefinition(
            class_name="TestClass",
            is_class_method=False,
            selector="longMethod",
            body=long_body,
            metadata={"category": "#someCategory"},
        )

        linter = TonelLinter()
        issues = linter._check_method_length(method)

        # Should warn about long method
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "long:" in issues[0].message

    def test_check_method_length_error(self):
        """Test method length checking with error threshold."""
        from tonel_smalltalk_parser.tonel_parser import MethodDefinition

        # Create a very long method (30 lines)
        long_body = "\n".join([f"    line{i} := {i}." for i in range(30)])
        method = MethodDefinition(
            class_name="TestClass",
            is_class_method=False,
            selector="veryLongMethod",
            body=long_body,
            metadata={"category": "#someCategory"},
        )

        linter = TonelLinter()
        issues = linter._check_method_length(method)

        # Should error about very long method
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "too long:" in issues[0].message

    def test_check_direct_access(self):
        """Test direct instance variable access checking."""
        from tonel_smalltalk_parser.tonel_parser import MethodDefinition

        # Method with direct access
        method = MethodDefinition(
            class_name="TestClass",
            is_class_method=False,
            selector="badMethod",
            body="    var1 := 42.\n    ^ var1",
            metadata={"category": "#someCategory"},
        )

        inst_vars = {"var1"}

        linter = TonelLinter()
        issues = linter._check_direct_access(method, inst_vars)

        # Should warn about direct access (2 instances: assignment and return)
        assert len(issues) == 2
        assert all(issue.severity == "warning" for issue in issues)
        assert all("Direct access" in issue.message for issue in issues)

    def test_check_direct_access_in_accessor(self):
        """Test that direct access is allowed in accessor methods."""
        from tonel_smalltalk_parser.tonel_parser import MethodDefinition

        # Accessor method with direct access (should be allowed)
        method = MethodDefinition(
            class_name="TestClass",
            is_class_method=False,
            selector="var1:",
            body="    var1 := aValue",
            metadata={"category": "#accessing"},
        )

        inst_vars = {"var1"}

        linter = TonelLinter()
        issues = linter._check_direct_access(method, inst_vars)

        # Should have no issues for accessor methods
        assert len(issues) == 0

    def test_print_summary(self):
        """Test summary printing."""
        linter = TonelLinter()
        linter.warnings = 2
        linter.errors = 1

        # Capture print output would require more complex setup
        # For now, just test the return value
        exit_code = linter.print_summary(5)
        assert exit_code == 2  # errors > 0

    def test_print_summary_warnings_only(self):
        """Test summary printing with warnings only."""
        linter = TonelLinter()
        linter.warnings = 2
        linter.errors = 0

        exit_code = linter.print_summary(5)
        assert exit_code == 1  # warnings > 0, errors == 0

    def test_print_summary_clean(self):
        """Test summary printing with no issues."""
        linter = TonelLinter()
        linter.warnings = 0
        linter.errors = 0

        exit_code = linter.print_summary(5)
        assert exit_code == 0  # no issues
