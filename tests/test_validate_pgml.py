#!/usr/bin/env python3

"""Tests for validate_pgml module."""

# Standard Library
import os
import sys

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import validate_pgml

# minimal valid PGML source
VALID_SOURCE = (
	"DOCUMENT();\n"
	"loadMacros('PGstandard.pl', 'PGML.pl');\n"
	'Context("Numeric");\n'
	"$answer = Compute('42');\n"
	"BEGIN_PGML\n"
	"What is the answer? [_____]{$answer}\n"
	"END_PGML\n"
	"BEGIN_PGML_SOLUTION\n"
	"The answer is 42.\n"
	"END_PGML_SOLUTION\n"
	"ENDDOCUMENT();\n"
)


#============================================
class TestCheckAsciiCompliance:
	"""Tests for check_ascii_compliance function."""

	#============================================
	def test_ascii_only(self):
		"""Test that pure ASCII source produces no issues."""
		issues = validate_pgml.check_ascii_compliance("hello world\n")
		assert len(issues) == 0

	#============================================
	def test_non_ascii_detected(self):
		"""Test that non-ASCII character is detected."""
		# euro sign is U+20AC
		source = "price = \u20ac100\n"
		issues = validate_pgml.check_ascii_compliance(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "ascii_compliance"
		assert issues[0]["severity"] == "error"
		assert "U+20AC" in issues[0]["message"]

	#============================================
	def test_only_first_per_line(self):
		"""Test that only first non-ASCII per line is reported."""
		source = "\u00e9\u00e8\n"
		issues = validate_pgml.check_ascii_compliance(source)
		# should report only one issue for the line
		assert len(issues) == 1


#============================================
class TestCheckContextCall:
	"""Tests for check_context_call function."""

	#============================================
	def test_has_context(self):
		"""Test source with Context() produces no issues."""
		source = 'Context("Numeric");\n'
		issues = validate_pgml.check_context_call(source)
		assert len(issues) == 0

	#============================================
	def test_missing_context(self):
		"""Test source without Context() produces warning."""
		source = "$x = 42;\n"
		issues = validate_pgml.check_context_call(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "context_call"
		assert issues[0]["severity"] == "warning"


#============================================
class TestCheckLoadMacros:
	"""Tests for check_load_macros function."""

	#============================================
	def test_has_load_macros(self):
		"""Test source with loadMacros() produces no issues."""
		source = "loadMacros('PGstandard.pl');\n"
		issues = validate_pgml.check_load_macros(source)
		assert len(issues) == 0

	#============================================
	def test_missing_load_macros(self):
		"""Test source without loadMacros() produces error."""
		source = "$x = 42;\n"
		issues = validate_pgml.check_load_macros(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "load_macros"
		assert issues[0]["severity"] == "error"


#============================================
class TestCheckSolutionPresent:
	"""Tests for check_solution_present function."""

	#============================================
	def test_has_solution(self):
		"""Test source with solution produces no issues."""
		source = "BEGIN_PGML_SOLUTION\nAnswer\nEND_PGML_SOLUTION\n"
		issues = validate_pgml.check_solution_present(source)
		assert len(issues) == 0

	#============================================
	def test_missing_solution(self):
		"""Test source without solution produces warning."""
		source = "BEGIN_PGML\nQuestion\nEND_PGML\n"
		issues = validate_pgml.check_solution_present(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "solution_present"
		assert issues[0]["severity"] == "warning"


#============================================
class TestValidateSource:
	"""Tests for validate_source function."""

	#============================================
	def test_valid_source_minimal_issues(self):
		"""Test that valid complete source produces no errors."""
		issues = validate_pgml.validate_source(VALID_SOURCE)
		# filter to errors only (warnings may exist)
		errors = [i for i in issues if i["severity"] == "error"]
		assert len(errors) == 0

	#============================================
	def test_issues_sorted_by_line(self):
		"""Test that returned issues are sorted by line number."""
		# source with multiple issues at different lines
		source = (
			"my $x = 1;\n"
			"<table>\n"
			"BEGIN_PGML\n"
			"[$x]\n"
			"END_PGML\n"
		)
		issues = validate_pgml.validate_source(source)
		line_numbers = [i["line"] for i in issues]
		assert line_numbers == sorted(line_numbers)


#============================================
class TestValidateFile:
	"""Tests for validate_file function."""

	#============================================
	def test_validate_valid_file(self, tmp_path):
		"""Test validating a valid .pgml file from disk."""
		pgml_file = tmp_path / "test_valid.pgml"
		pgml_file.write_text(VALID_SOURCE, encoding="utf-8")
		issues = validate_pgml.validate_file(str(pgml_file))
		# all issues should have 'file' key
		for issue in issues:
			assert "file" in issue
			assert str(pgml_file) in issue["file"]

	#============================================
	def test_validate_bad_file(self, tmp_path):
		"""Test validating a bad .pgml file from disk."""
		bad_content = "my $x = 1;\n<table>\n"
		pgml_file = tmp_path / "test_bad.pgml"
		pgml_file.write_text(bad_content, encoding="utf-8")
		issues = validate_pgml.validate_file(str(pgml_file))
		assert len(issues) > 0
		# should have file key on every issue
		for issue in issues:
			assert "file" in issue


#============================================
class TestValidateDirectory:
	"""Tests for validate_directory function."""

	#============================================
	def test_validate_empty_directory(self, tmp_path):
		"""Test validating directory with no .pgml files."""
		results = validate_pgml.validate_directory(str(tmp_path))
		assert len(results) == 0

	#============================================
	def test_validate_directory_with_files(self, tmp_path):
		"""Test validating directory with multiple .pgml files."""
		# create two pgml files
		file1 = tmp_path / "q1.pgml"
		file1.write_text(VALID_SOURCE, encoding="utf-8")
		file2 = tmp_path / "q2.pgml"
		file2.write_text("my $x = 1;\n", encoding="utf-8")
		results = validate_pgml.validate_directory(str(tmp_path))
		assert len(results) == 2
		# each key should be a file path string
		for file_path in results:
			assert isinstance(results[file_path], list)

	#============================================
	def test_validate_nested_directory(self, tmp_path):
		"""Test that nested .pgml files are found recursively."""
		subdir = tmp_path / "ch01"
		subdir.mkdir()
		pgml_file = subdir / "q1.pgml"
		pgml_file.write_text(VALID_SOURCE, encoding="utf-8")
		results = validate_pgml.validate_directory(str(tmp_path))
		assert len(results) == 1


#============================================
class TestFormatIssue:
	"""Tests for format_issue function."""

	#============================================
	def test_format_basic_issue(self):
		"""Test formatting a basic issue dict."""
		issue = {
			"file": "test.pgml",
			"line": 5,
			"check": "structure",
			"severity": "error",
			"message": "Missing DOCUMENT()",
		}
		result = validate_pgml.format_issue(issue)
		assert "test.pgml:5" in result
		assert "[ERROR]" in result
		assert "structure" in result
		assert "Missing DOCUMENT()" in result

	#============================================
	def test_format_warning_issue(self):
		"""Test formatting a warning-level issue."""
		issue = {
			"file": "test.pgml",
			"line": 1,
			"check": "context_call",
			"severity": "warning",
			"message": "No Context() call",
		}
		result = validate_pgml.format_issue(issue)
		assert "[WARNING]" in result
