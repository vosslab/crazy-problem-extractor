#!/usr/bin/env python3

"""Utilities for mapping PGML widgets to their required WeBWorK macros."""

# Standard Library
import re

# Widget name -> required .pl macro filename
WIDGET_MACRO_MAP: dict = {
	"RadioButtons": "parserRadioButtons.pl",
	"PopUp": "parserPopUp.pl",
	"DropDown": "parserPopUp.pl",
	"DropDownTF": "parserPopUp.pl",
	"niceTables": "niceTables.pl",
	"DataTable": "niceTables.pl",
	"LayoutTable": "niceTables.pl",
	"CheckboxList": "parserCheckboxList.pl",
	"MultiAnswer": "parserMultiAnswer.pl",
}

#============================================
def macro_for_widget(widget_name: str) -> str:
	"""Return the required .pl macro filename for a given widget name.

	Args:
		widget_name: name of the PGML widget (e.g. 'RadioButtons').

	Returns:
		The macro filename string, or empty string if not recognized.
	"""
	macro_name = WIDGET_MACRO_MAP.get(widget_name, "")
	return macro_name

#============================================
def detect_widgets_used(source: str) -> list:
	"""Scan PGML source text for widget constructor calls.

	Looks for patterns like RadioButtons(...), PopUp(...), DropDown(...),
	DataTable(...), CheckboxList(...), etc.

	Args:
		source: the full PGML/PG source code as a string.

	Returns:
		Sorted list of unique widget names found in the source.
	"""
	# Build pattern from known widget names
	widget_names = list(WIDGET_MACRO_MAP.keys())
	# Match WidgetName followed by opening paren
	pattern = r'\b(' + '|'.join(re.escape(w) for w in widget_names) + r')\s*\('
	matches = re.findall(pattern, source)
	# Return sorted unique list
	found = sorted(set(matches))
	return found

#============================================
def extract_loaded_macros(source: str) -> list:
	"""Extract macro filenames from a loadMacros() call in the source.

	Parses the loadMacros(...) block to find all quoted .pl filenames.

	Args:
		source: the full PGML/PG source code as a string.

	Returns:
		List of macro filename strings found inside loadMacros().
	"""
	# Find the loadMacros(...) block, allowing multiline content
	load_match = re.search(r'loadMacros\s*\((.*?)\)', source, re.DOTALL)
	if not load_match:
		return []
	# Extract quoted strings ending in .pl from inside the parens
	inner_text = load_match.group(1)
	macros = re.findall(r'["\']([^"\']+\.pl)["\']', inner_text)
	return macros

#============================================
def validate_macro_widget_pairing(source: str) -> list:
	"""Check that loadMacros includes the required macro for each widget used.

	For each widget detected in the source, verify that the corresponding
	macro file is listed in the loadMacros() call.

	Args:
		source: the full PGML/PG source code as a string.

	Returns:
		List of error dicts with keys: line, check, message, severity.
	"""
	errors = []
	widgets = detect_widgets_used(source)
	loaded = extract_loaded_macros(source)
	for widget in widgets:
		required_macro = macro_for_widget(widget)
		if not required_macro:
			# Unknown widget, skip
			continue
		if required_macro not in loaded:
			# Find the line number where the widget is first used
			line_num = 0
			for i, line in enumerate(source.splitlines(), start=1):
				if re.search(r'\b' + re.escape(widget) + r'\s*\(', line):
					line_num = i
					break
			error = {
				"line": line_num,
				"check": "macro_widget_pairing",
				"message": f"Widget '{widget}' requires '{required_macro}' in loadMacros()",
				"severity": "error",
			}
			errors.append(error)
	return errors

#============================================
def main() -> None:
	"""Run assert tests for all functions."""

	# Test macro_for_widget for each known widget
	assert macro_for_widget("RadioButtons") == "parserRadioButtons.pl"
	assert macro_for_widget("PopUp") == "parserPopUp.pl"
	assert macro_for_widget("DropDown") == "parserPopUp.pl"
	assert macro_for_widget("DropDownTF") == "parserPopUp.pl"
	assert macro_for_widget("niceTables") == "niceTables.pl"
	assert macro_for_widget("DataTable") == "niceTables.pl"
	assert macro_for_widget("LayoutTable") == "niceTables.pl"
	assert macro_for_widget("CheckboxList") == "parserCheckboxList.pl"
	assert macro_for_widget("MultiAnswer") == "parserMultiAnswer.pl"
	assert macro_for_widget("UnknownWidget") == ""
	print("macro_for_widget: all tests passed")

	# Test detect_widgets_used with sample source
	sample_source = """
$radio = RadioButtons(["True", "False"]);
$popup = PopUp(["A", "B"]);
$table = DataTable([]);
"""
	detected = detect_widgets_used(sample_source)
	assert "RadioButtons" in detected
	assert "PopUp" in detected
	assert "DataTable" in detected
	assert len(detected) == 3
	print("detect_widgets_used: all tests passed")

	# Test extract_loaded_macros
	macro_source = """
loadMacros(
  "PGstandard.pl",
  "parserRadioButtons.pl",
  "niceTables.pl",
);
"""
	loaded = extract_loaded_macros(macro_source)
	assert "PGstandard.pl" in loaded
	assert "parserRadioButtons.pl" in loaded
	assert "niceTables.pl" in loaded
	assert len(loaded) == 3
	print("extract_loaded_macros: all tests passed")

	# Test validate_macro_widget_pairing with valid source (no errors)
	valid_source = """
loadMacros(
  "PGstandard.pl",
  "parserRadioButtons.pl",
);
$radio = RadioButtons(["True", "False"]);
"""
	errors = validate_macro_widget_pairing(valid_source)
	assert len(errors) == 0
	print("validate_macro_widget_pairing (valid): all tests passed")

	# Test validate_macro_widget_pairing with missing macro (should error)
	invalid_source = """
loadMacros(
  "PGstandard.pl",
);
$radio = RadioButtons(["True", "False"]);
"""
	errors = validate_macro_widget_pairing(invalid_source)
	assert len(errors) == 1
	assert errors[0]["check"] == "macro_widget_pairing"
	assert "RadioButtons" in errors[0]["message"]
	assert "parserRadioButtons.pl" in errors[0]["message"]
	assert errors[0]["severity"] == "error"
	print("validate_macro_widget_pairing (invalid): all tests passed")

	print("All pgml_macros tests passed.")

#============================================
if __name__ == '__main__':
	main()
