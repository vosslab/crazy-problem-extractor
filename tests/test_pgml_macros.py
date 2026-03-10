#!/usr/bin/env python3

"""Tests for pgml_macros module."""

# Standard Library
import os
import sys

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import pgml_macros


#============================================
class TestMacroForWidget:
	"""Tests for macro_for_widget function."""

	#============================================
	def test_radio_buttons(self):
		"""Test RadioButtons maps to parserRadioButtons.pl."""
		result = pgml_macros.macro_for_widget("RadioButtons")
		assert result == "parserRadioButtons.pl"

	#============================================
	def test_popup(self):
		"""Test PopUp maps to parserPopUp.pl."""
		result = pgml_macros.macro_for_widget("PopUp")
		assert result == "parserPopUp.pl"

	#============================================
	def test_dropdown(self):
		"""Test DropDown maps to parserPopUp.pl."""
		result = pgml_macros.macro_for_widget("DropDown")
		assert result == "parserPopUp.pl"

	#============================================
	def test_dropdown_tf(self):
		"""Test DropDownTF maps to parserPopUp.pl."""
		result = pgml_macros.macro_for_widget("DropDownTF")
		assert result == "parserPopUp.pl"

	#============================================
	def test_nice_tables(self):
		"""Test niceTables maps to niceTables.pl."""
		result = pgml_macros.macro_for_widget("niceTables")
		assert result == "niceTables.pl"

	#============================================
	def test_data_table(self):
		"""Test DataTable maps to niceTables.pl."""
		result = pgml_macros.macro_for_widget("DataTable")
		assert result == "niceTables.pl"

	#============================================
	def test_layout_table(self):
		"""Test LayoutTable maps to niceTables.pl."""
		result = pgml_macros.macro_for_widget("LayoutTable")
		assert result == "niceTables.pl"

	#============================================
	def test_checkbox_list(self):
		"""Test CheckboxList maps to parserCheckboxList.pl."""
		result = pgml_macros.macro_for_widget("CheckboxList")
		assert result == "parserCheckboxList.pl"

	#============================================
	def test_multi_answer(self):
		"""Test MultiAnswer maps to parserMultiAnswer.pl."""
		result = pgml_macros.macro_for_widget("MultiAnswer")
		assert result == "parserMultiAnswer.pl"

	#============================================
	def test_unknown_widget(self):
		"""Test unknown widget returns empty string."""
		result = pgml_macros.macro_for_widget("UnknownWidget")
		assert result == ""


#============================================
class TestDetectWidgetsUsed:
	"""Tests for detect_widgets_used function."""

	#============================================
	def test_detects_multiple_widgets(self):
		"""Test detection of multiple widget types in source."""
		source = (
			'$radio = RadioButtons(["True", "False"]);\n'
			'$popup = PopUp(["A", "B"]);\n'
			'$table = DataTable([]);\n'
		)
		detected = pgml_macros.detect_widgets_used(source)
		assert "RadioButtons" in detected
		assert "PopUp" in detected
		assert "DataTable" in detected
		assert len(detected) == 3

	#============================================
	def test_no_widgets(self):
		"""Test that source with no widgets returns empty list."""
		source = "$x = 42;\n"
		detected = pgml_macros.detect_widgets_used(source)
		assert len(detected) == 0

	#============================================
	def test_returns_sorted_unique(self):
		"""Test that result is sorted and deduplicated."""
		source = (
			'$a = PopUp(["X"]);\n'
			'$b = PopUp(["Y"]);\n'
			'$c = DataTable([]);\n'
		)
		detected = pgml_macros.detect_widgets_used(source)
		assert detected == sorted(set(detected))
		# PopUp should appear only once
		assert detected.count("PopUp") == 1


#============================================
class TestExtractLoadedMacros:
	"""Tests for extract_loaded_macros function."""

	#============================================
	def test_extracts_macros(self):
		"""Test extraction of macro filenames from loadMacros block."""
		source = (
			'loadMacros(\n'
			'  "PGstandard.pl",\n'
			'  "parserRadioButtons.pl",\n'
			'  "niceTables.pl",\n'
			');\n'
		)
		loaded = pgml_macros.extract_loaded_macros(source)
		assert "PGstandard.pl" in loaded
		assert "parserRadioButtons.pl" in loaded
		assert "niceTables.pl" in loaded
		assert len(loaded) == 3

	#============================================
	def test_no_load_macros(self):
		"""Test returns empty list when no loadMacros found."""
		source = "$x = 42;\n"
		loaded = pgml_macros.extract_loaded_macros(source)
		assert len(loaded) == 0

	#============================================
	def test_single_quoted_macros(self):
		"""Test extraction with single-quoted macro names."""
		source = "loadMacros('PGstandard.pl', 'PGML.pl');\n"
		loaded = pgml_macros.extract_loaded_macros(source)
		assert "PGstandard.pl" in loaded
		assert "PGML.pl" in loaded


#============================================
class TestValidateMacroWidgetPairing:
	"""Tests for validate_macro_widget_pairing function."""

	#============================================
	def test_valid_pairing_no_errors(self):
		"""Test valid pairing produces no errors."""
		source = (
			'loadMacros(\n'
			'  "PGstandard.pl",\n'
			'  "parserRadioButtons.pl",\n'
			');\n'
			'$radio = RadioButtons(["True", "False"]);\n'
		)
		errors = pgml_macros.validate_macro_widget_pairing(source)
		assert len(errors) == 0

	#============================================
	def test_missing_macro_produces_error(self):
		"""Test that missing macro for widget produces error."""
		source = (
			'loadMacros(\n'
			'  "PGstandard.pl",\n'
			');\n'
			'$radio = RadioButtons(["True", "False"]);\n'
		)
		errors = pgml_macros.validate_macro_widget_pairing(source)
		assert len(errors) == 1
		assert errors[0]["check"] == "macro_widget_pairing"
		assert "RadioButtons" in errors[0]["message"]
		assert "parserRadioButtons.pl" in errors[0]["message"]
		assert errors[0]["severity"] == "error"

	#============================================
	def test_error_has_line_number(self):
		"""Test that error includes a line number."""
		source = (
			'loadMacros("PGstandard.pl");\n'
			'$popup = PopUp(["A", "B"]);\n'
		)
		errors = pgml_macros.validate_macro_widget_pairing(source)
		assert len(errors) == 1
		assert errors[0]["line"] == 2

	#============================================
	def test_no_widgets_no_errors(self):
		"""Test that source with no widgets produces no errors."""
		source = 'loadMacros("PGstandard.pl");\n$x = 42;\n'
		errors = pgml_macros.validate_macro_widget_pairing(source)
		assert len(errors) == 0
