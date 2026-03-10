#!/usr/bin/env python3

"""Tests for pgml_template module."""

# Standard Library
import os
import sys

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import pgml_template


#============================================
class TestBuildHeaderBlock:
	"""Tests for build_header_block function."""

	#============================================
	def test_basic_header(self):
		"""Test that a basic header contains all expected OPL fields."""
		header = pgml_template.build_header_block(
			title="Test Title",
			description="test description",
			keywords="keyword1, keyword2",
			db_subject="Biology",
			db_chapter="Biochemistry",
			db_section="Amino Acids",
			level=2,
			author="Test Author",
			institution="TST",
		)
		assert "## DBsubject(Biology)" in header
		assert "## DBchapter(Biochemistry)" in header
		assert "## DBsection(Amino Acids)" in header
		assert "## Level(2)" in header
		assert "## KEYWORDS('keyword1, keyword2')" in header
		assert "## TitleText1('Test Title')" in header
		assert "## AuthorText1('Test Author')" in header
		assert "## Author(Test Author)" in header
		assert "## Institution(TST)" in header

	#============================================
	def test_header_line_count(self):
		"""Test that header has expected number of lines."""
		header = pgml_template.build_header_block(
			title="T", description="D", keywords="K",
			db_subject="S", db_chapter="C", db_section="Sec",
			level=1, author="A", institution="I",
		)
		lines = header.strip().splitlines()
		# 9 lines: DBsubject, DBchapter, DBsection, Level, KEYWORDS,
		#          TitleText1, AuthorText1, Author, Institution
		assert len(lines) == 9

	#============================================
	def test_header_level_values(self):
		"""Test header with different level values."""
		for level in (1, 3, 5):
			header = pgml_template.build_header_block(
				title="T", description="D", keywords="K",
				db_subject="S", db_chapter="C", db_section="Sec",
				level=level, author="A", institution="I",
			)
			assert f"## Level({level})" in header

	#============================================
	def test_header_returns_string(self):
		"""Test that build_header_block returns a string."""
		result = pgml_template.build_header_block(
			title="T", description="D", keywords="K",
			db_subject="S", db_chapter="C", db_section="Sec",
			level=1, author="A", institution="I",
		)
		assert isinstance(result, str)


#============================================
class TestBuildPreamble:
	"""Tests for build_preamble function."""

	#============================================
	def test_preamble_required_macros(self):
		"""Test that preamble always includes PGstandard.pl and PGML.pl."""
		preamble = pgml_template.build_preamble([])
		assert '"PGstandard.pl"' in preamble
		assert '"PGML.pl"' in preamble

	#============================================
	def test_preamble_document_call(self):
		"""Test that preamble starts with DOCUMENT()."""
		preamble = pgml_template.build_preamble([])
		assert "DOCUMENT();" in preamble

	#============================================
	def test_preamble_load_macros_block(self):
		"""Test that preamble includes loadMacros block."""
		preamble = pgml_template.build_preamble([])
		assert "loadMacros(" in preamble

	#============================================
	def test_preamble_context_numeric(self):
		"""Test that preamble includes Context(Numeric)."""
		preamble = pgml_template.build_preamble([])
		assert 'Context("Numeric");' in preamble

	#============================================
	def test_preamble_rng_setup(self):
		"""Test that preamble includes PGrandom setup."""
		preamble = pgml_template.build_preamble([])
		assert "$rng = PGrandom->new();" in preamble
		assert "$rng->srand($problemSeed);" in preamble

	#============================================
	def test_preamble_additional_macro(self):
		"""Test that additional macros are included."""
		preamble = pgml_template.build_preamble(["parserRadioButtons.pl"])
		assert '"parserRadioButtons.pl"' in preamble

	#============================================
	def test_preamble_dedup_required_macros(self):
		"""Test that required macros are not duplicated when passed again."""
		preamble = pgml_template.build_preamble(["PGstandard.pl", "PGML.pl", "extra.pl"])
		count_pgstandard = preamble.count("PGstandard.pl")
		count_pgml = preamble.count("PGML.pl")
		assert count_pgstandard == 1
		assert count_pgml == 1
		assert '"extra.pl"' in preamble

	#============================================
	def test_preamble_empty_macros_list(self):
		"""Test preamble with empty macro list still works."""
		preamble = pgml_template.build_preamble([])
		assert isinstance(preamble, str)
		assert len(preamble) > 0


#============================================
class TestBuildSolutionBlock:
	"""Tests for build_solution_block function."""

	#============================================
	def test_solution_wraps_text(self):
		"""Test that solution block wraps explanation text."""
		solution = pgml_template.build_solution_block("The answer is 42.")
		assert "BEGIN_PGML_SOLUTION" in solution
		assert "The answer is 42." in solution
		assert "END_PGML_SOLUTION" in solution

	#============================================
	def test_solution_ordering(self):
		"""Test that BEGIN comes before explanation which comes before END."""
		solution = pgml_template.build_solution_block("Explanation here.")
		lines = solution.splitlines()
		assert lines[0] == "BEGIN_PGML_SOLUTION"
		assert lines[1] == "Explanation here."
		assert lines[2] == "END_PGML_SOLUTION"

	#============================================
	def test_solution_empty_explanation(self):
		"""Test solution block with empty explanation string."""
		solution = pgml_template.build_solution_block("")
		assert "BEGIN_PGML_SOLUTION" in solution
		assert "END_PGML_SOLUTION" in solution


#============================================
class TestBuildFooter:
	"""Tests for build_footer function."""

	#============================================
	def test_footer_value(self):
		"""Test that footer returns ENDDOCUMENT();."""
		footer = pgml_template.build_footer()
		assert footer == "ENDDOCUMENT();"

	#============================================
	def test_footer_returns_string(self):
		"""Test that footer returns a string type."""
		footer = pgml_template.build_footer()
		assert isinstance(footer, str)
