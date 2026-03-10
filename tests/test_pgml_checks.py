#!/usr/bin/env python3

"""Tests for pgml_checks module."""

# Standard Library
import os
import sys

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import pgml_checks

# known-good PGML source that passes all checks
VALID_SOURCE = (
	"DOCUMENT();\n"
	"loadMacros('PGstandard.pl', 'PGML.pl');\n"
	"$answer = Compute('42');\n"
	"BEGIN_PGML\n"
	"What is the answer? [_____]{$answer}\n"
	"END_PGML\n"
	"ENDDOCUMENT();\n"
)

# known-bad PGML source with multiple deliberate issues
BAD_SOURCE = (
	"DOCUMENT();\n"
	"loadMacros('PGstandard.pl', 'PGML.pl');\n"
	"TEXT(beginproblem());\n"
	"my $answer = Compute('42');\n"
	"my $html_table = '<table><tr><td>data</td></tr></table>';\n"
	"BEGIN_PGML\n"
	"Here is the table: [$html_table]\n"
	"Color: [``\\color{red} x``]\n"
	"Fill in the blank: [____]\n"
	"END_PGML\n"
	"ENDDOCUMENT();\n"
)


#============================================
class TestCheckHtmlWhitelist:
	"""Tests for check_html_whitelist function."""

	#============================================
	def test_no_blocked_tags(self):
		"""Test clean source produces no issues."""
		issues = pgml_checks.check_html_whitelist(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_detects_table_tag(self):
		"""Test detection of blocked <table> tag."""
		source = "some text <table> more\n"
		issues = pgml_checks.check_html_whitelist(source)
		assert len(issues) >= 1
		assert issues[0]["check"] == "html_whitelist"
		assert issues[0]["severity"] == "error"

	#============================================
	def test_detects_td_tag(self):
		"""Test detection of blocked <td> tag."""
		source = "<td>cell</td>\n"
		issues = pgml_checks.check_html_whitelist(source)
		assert len(issues) >= 1

	#============================================
	def test_detects_closing_tags(self):
		"""Test detection of closing table tags."""
		source = "</table></tr>\n"
		issues = pgml_checks.check_html_whitelist(source)
		assert len(issues) >= 2


#============================================
class TestCheckRawPassthrough:
	"""Tests for check_raw_passthrough function."""

	#============================================
	def test_no_issues_with_asterisk(self):
		"""Test that [$var]* does not trigger warning."""
		source = "[$html_table]*\n"
		issues = pgml_checks.check_raw_passthrough(source)
		assert len(issues) == 0

	#============================================
	def test_warns_without_asterisk(self):
		"""Test that [$var] without * triggers warning."""
		source = "[$html_table]\n"
		issues = pgml_checks.check_raw_passthrough(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "raw_passthrough"
		assert issues[0]["severity"] == "warning"

	#============================================
	def test_clean_source_no_issues(self):
		"""Test clean source with grader blanks produces no passthrough warnings."""
		# grader blanks like [_____]{$answer} should not trigger
		source = "[_____]{$answer}\n"
		issues = pgml_checks.check_raw_passthrough(source)
		assert len(issues) == 0


#============================================
class TestCheckColorUsage:
	"""Tests for check_color_usage function."""

	#============================================
	def test_no_color_macros(self):
		"""Test clean source has no color warnings."""
		issues = pgml_checks.check_color_usage(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_detects_color_macro(self):
		"""Test detection of \\color{} macro."""
		source = "\\color{red}\n"
		issues = pgml_checks.check_color_usage(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "color_usage"
		assert issues[0]["severity"] == "warning"

	#============================================
	def test_detects_textcolor_macro(self):
		"""Test detection of \\textcolor{} macro."""
		source = "\\textcolor{blue}\n"
		issues = pgml_checks.check_color_usage(source)
		assert len(issues) == 1


#============================================
class TestCheckVariableScoping:
	"""Tests for check_variable_scoping function."""

	#============================================
	def test_no_my_keyword(self):
		"""Test source without 'my' keyword has no issues."""
		issues = pgml_checks.check_variable_scoping(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_detects_my_keyword(self):
		"""Test detection of 'my $var' pattern."""
		source = "my $answer = 42;\n"
		issues = pgml_checks.check_variable_scoping(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "variable_scoping"
		assert "answer" in issues[0]["message"]

	#============================================
	def test_multiple_my_vars(self):
		"""Test detection of multiple 'my' variables."""
		source = "my $a = 1;\nmy $b = 2;\n"
		issues = pgml_checks.check_variable_scoping(source)
		assert len(issues) == 2


#============================================
class TestCheckStructure:
	"""Tests for check_structure function."""

	#============================================
	def test_valid_structure(self):
		"""Test valid source has no structure issues."""
		issues = pgml_checks.check_structure(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_missing_document(self):
		"""Test detection of missing DOCUMENT() call."""
		source = (
			"loadMacros('PGstandard.pl');\n"
			"BEGIN_PGML\nHello\nEND_PGML\n"
		)
		issues = pgml_checks.check_structure(source)
		msgs = [i["message"] for i in issues]
		assert any("Missing DOCUMENT()" in m for m in msgs)
		assert any("Missing ENDDOCUMENT()" in m for m in msgs)

	#============================================
	def test_missing_pgml_block(self):
		"""Test detection of missing BEGIN_PGML block."""
		source = "DOCUMENT();\nENDDOCUMENT();\n"
		issues = pgml_checks.check_structure(source)
		msgs = [i["message"] for i in issues]
		assert any("No BEGIN_PGML block" in m for m in msgs)

	#============================================
	def test_mismatched_pgml_blocks(self):
		"""Test detection of mismatched BEGIN/END PGML."""
		source = (
			"DOCUMENT();\n"
			"BEGIN_PGML\nHello\nBEGIN_PGML\nWorld\nEND_PGML\n"
			"ENDDOCUMENT();\n"
		)
		issues = pgml_checks.check_structure(source)
		msgs = [i["message"] for i in issues]
		assert any("Mismatched BEGIN_PGML" in m for m in msgs)

	#============================================
	def test_mismatched_solution_blocks(self):
		"""Test detection of mismatched solution blocks."""
		source = (
			"DOCUMENT();\n"
			"BEGIN_PGML\nQ\nEND_PGML\n"
			"BEGIN_PGML_SOLUTION\nA\n"
			"ENDDOCUMENT();\n"
		)
		issues = pgml_checks.check_structure(source)
		msgs = [i["message"] for i in issues]
		assert any("Mismatched BEGIN_PGML_SOLUTION" in m for m in msgs)

	#============================================
	def test_duplicate_document(self):
		"""Test detection of multiple DOCUMENT() calls."""
		source = (
			"DOCUMENT();\nDOCUMENT();\n"
			"BEGIN_PGML\nQ\nEND_PGML\n"
			"ENDDOCUMENT();\n"
		)
		issues = pgml_checks.check_structure(source)
		msgs = [i["message"] for i in issues]
		assert any("Found 2 DOCUMENT()" in m for m in msgs)


#============================================
class TestCheckInlineGraders:
	"""Tests for check_inline_graders function."""

	#============================================
	def test_valid_grader(self):
		"""Test blank with grader produces no issue."""
		source = "[_____]{$answer}\n"
		issues = pgml_checks.check_inline_graders(source)
		assert len(issues) == 0

	#============================================
	def test_missing_grader(self):
		"""Test blank without grader is detected."""
		source = "[____]\n"
		issues = pgml_checks.check_inline_graders(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "inline_graders"
		assert issues[0]["severity"] == "error"


#============================================
class TestCheckNoBeginproblem:
	"""Tests for check_no_beginproblem function."""

	#============================================
	def test_no_beginproblem(self):
		"""Test clean source has no beginproblem issues."""
		issues = pgml_checks.check_no_beginproblem(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_detects_beginproblem(self):
		"""Test detection of TEXT(beginproblem()) call."""
		source = "TEXT(beginproblem());\n"
		issues = pgml_checks.check_no_beginproblem(source)
		assert len(issues) == 1
		assert issues[0]["check"] == "no_beginproblem"
		assert issues[0]["severity"] == "error"


#============================================
class TestRunAllChecks:
	"""Tests for run_all_checks function."""

	#============================================
	def test_valid_source_no_issues(self):
		"""Test that valid source produces zero issues."""
		issues = pgml_checks.run_all_checks(VALID_SOURCE)
		assert len(issues) == 0

	#============================================
	def test_bad_source_fires_expected_checks(self):
		"""Test that bad source triggers all expected check categories."""
		issues = pgml_checks.run_all_checks(BAD_SOURCE)
		check_names = set(i["check"] for i in issues)
		assert "no_beginproblem" in check_names
		assert "variable_scoping" in check_names
		assert "html_whitelist" in check_names
		assert "raw_passthrough" in check_names
		assert "color_usage" in check_names
		assert "inline_graders" in check_names

	#============================================
	def test_issue_dict_structure(self):
		"""Test that all issue dicts have required keys."""
		issues = pgml_checks.run_all_checks(BAD_SOURCE)
		for issue in issues:
			assert "line" in issue
			assert "check" in issue
			assert "message" in issue
			assert "severity" in issue
			assert issue["severity"] in ("error", "warning")
			assert isinstance(issue["line"], int)
