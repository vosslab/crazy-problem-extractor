#!/usr/bin/env python3

"""
PGML source file checks for common issues and anti-patterns.

Each check function takes the full source text of a .pgml file
and returns a list of issue dicts with keys:
  line, check, message, severity
"""

# Standard Library
import re

#============================================
def check_html_whitelist(source: str) -> list:
	"""Detect blocked HTML tags that should use niceTables.pl instead.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts for each blocked tag found.
	"""
	issues = []
	# blocked tags: table, tr, td, th and their closing variants
	blocked_pattern = re.compile(r'<\s*/?\s*(table|tr|td|th)\b', re.IGNORECASE)
	for line_num, line in enumerate(source.splitlines(), start=1):
		for match in blocked_pattern.finditer(line):
			tag_name = match.group(1).lower()
			issue = {
				"line": line_num,
				"check": "html_whitelist",
				"message": f"Blocked HTML tag <{tag_name}> found; use niceTables.pl macro instead",
				"severity": "error",
			}
			issues.append(issue)
	return issues

#============================================
def check_raw_passthrough(source: str) -> list:
	"""Detect [$var] patterns that may need trailing asterisk for HTML passthrough.

	In PGML, variables containing HTML need a trailing asterisk: [$var]*

	Args:
		source: Full .pgml file content.

	Returns:
		List of warning dicts for suspicious [$var] without trailing *.
	"""
	issues = []
	# match [$var] NOT followed by *
	pattern = re.compile(r'\[\$\w+\](?!\*)')
	for line_num, line in enumerate(source.splitlines(), start=1):
		for match in pattern.finditer(line):
			var_text = match.group(0)
			issue = {
				"line": line_num,
				"check": "raw_passthrough",
				"message": f"{var_text} may need trailing asterisk for HTML passthrough: {var_text}*",
				"severity": "warning",
			}
			issues.append(issue)
	return issues

#============================================
def check_color_usage(source: str) -> list:
	"""Warn on MathJax color macros that should use HTML spans instead.

	Args:
		source: Full .pgml file content.

	Returns:
		List of warning dicts for color macro usage.
	"""
	issues = []
	# match \color{...} or \textcolor{...}
	pattern = re.compile(r'\\(color|textcolor)\s*\{')
	for line_num, line in enumerate(source.splitlines(), start=1):
		for match in pattern.finditer(line):
			macro_name = match.group(1)
			issue = {
				"line": line_num,
				"check": "color_usage",
				"message": f"\\{macro_name}{{}} found; prefer HTML <span> for color in PGML",
				"severity": "warning",
			}
			issues.append(issue)
	return issues

#============================================
def check_variable_scoping(source: str) -> list:
	"""Warn on 'my $var' for variables that may be PGML-visible.

	Variables used in PGML blocks should not use the 'my' keyword
	as it limits scope and can cause issues.

	Args:
		source: Full .pgml file content.

	Returns:
		List of warning dicts for 'my $' patterns.
	"""
	issues = []
	pattern = re.compile(r'\bmy\s+\$(\w+)')
	for line_num, line in enumerate(source.splitlines(), start=1):
		for match in pattern.finditer(line):
			var_name = match.group(1)
			issue = {
				"line": line_num,
				"check": "variable_scoping",
				"message": f"'my ${var_name}' may limit scope; PGML-visible vars should avoid 'my'",
				"severity": "warning",
			}
			issues.append(issue)
	return issues

#============================================
def check_structure(source: str) -> list:
	"""Check DOCUMENT/ENDDOCUMENT and BEGIN_PGML/END_PGML matching.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts for structural mismatches.
	"""
	issues = []
	lines = source.splitlines()

	# count DOCUMENT() and ENDDOCUMENT()
	doc_count = 0
	enddoc_count = 0
	for line_num, line in enumerate(lines, start=1):
		if re.search(r'\bDOCUMENT\s*\(\s*\)', line):
			doc_count += 1
		if re.search(r'\bENDDOCUMENT\s*\(\s*\)', line):
			enddoc_count += 1

	if doc_count == 0:
		issue = {
			"line": 1,
			"check": "structure",
			"message": "Missing DOCUMENT() call",
			"severity": "error",
		}
		issues.append(issue)
	elif doc_count > 1:
		issue = {
			"line": 1,
			"check": "structure",
			"message": f"Found {doc_count} DOCUMENT() calls; expected exactly 1",
			"severity": "error",
		}
		issues.append(issue)

	if enddoc_count == 0:
		issue = {
			"line": len(lines),
			"check": "structure",
			"message": "Missing ENDDOCUMENT() call",
			"severity": "error",
		}
		issues.append(issue)
	elif enddoc_count > 1:
		issue = {
			"line": len(lines),
			"check": "structure",
			"message": f"Found {enddoc_count} ENDDOCUMENT() calls; expected exactly 1",
			"severity": "error",
		}
		issues.append(issue)

	# count BEGIN_PGML / END_PGML pairs
	begin_pgml_count = 0
	end_pgml_count = 0
	for line in lines:
		if re.search(r'\bBEGIN_PGML\b(?!_)', line):
			begin_pgml_count += 1
		if re.search(r'\bEND_PGML\b(?!_)', line):
			end_pgml_count += 1

	if begin_pgml_count == 0:
		issue = {
			"line": 1,
			"check": "structure",
			"message": "No BEGIN_PGML block found; expected at least one",
			"severity": "error",
		}
		issues.append(issue)

	if begin_pgml_count != end_pgml_count:
		issue = {
			"line": 1,
			"check": "structure",
			"message": f"Mismatched BEGIN_PGML ({begin_pgml_count}) and END_PGML ({end_pgml_count})",
			"severity": "error",
		}
		issues.append(issue)

	# check BEGIN_PGML_SOLUTION / END_PGML_SOLUTION pairing
	begin_sol_count = 0
	end_sol_count = 0
	for line in lines:
		if re.search(r'\bBEGIN_PGML_SOLUTION\b', line):
			begin_sol_count += 1
		if re.search(r'\bEND_PGML_SOLUTION\b', line):
			end_sol_count += 1

	if begin_sol_count != end_sol_count:
		issue = {
			"line": 1,
			"check": "structure",
			"message": f"Mismatched BEGIN_PGML_SOLUTION ({begin_sol_count}) and END_PGML_SOLUTION ({end_sol_count})",
			"severity": "error",
		}
		issues.append(issue)

	return issues

#============================================
def check_inline_graders(source: str) -> list:
	"""Check that every [_]{} answer blank has a grader attached.

	In PGML, answer blanks look like [_____]{$answer}.
	Blanks without {$...} are likely missing their grader.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts for blanks missing graders.
	"""
	issues = []
	# match [_+] NOT followed by optional whitespace and {
	pattern = re.compile(r'\[_+\](?!\s*\{)')
	for line_num, line in enumerate(source.splitlines(), start=1):
		for match in pattern.finditer(line):
			issue = {
				"line": line_num,
				"check": "inline_graders",
				"message": f"Answer blank {match.group(0)} has no grader attached; expected {{$answer}}",
				"severity": "error",
			}
			issues.append(issue)
	return issues

#============================================
def check_no_beginproblem(source: str) -> list:
	"""Check that TEXT(beginproblem()) does not appear in the source.

	ADAPT handles beginproblem, so it should not be in .pgml source.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts if TEXT(beginproblem()) is found.
	"""
	issues = []
	pattern = re.compile(r'TEXT\s*\(\s*beginproblem\s*\(\s*\)\s*\)')
	for line_num, line in enumerate(source.splitlines(), start=1):
		if pattern.search(line):
			issue = {
				"line": line_num,
				"check": "no_beginproblem",
				"message": "TEXT(beginproblem()) found; ADAPT handles this automatically",
				"severity": "error",
			}
			issues.append(issue)
	return issues

#============================================
def run_all_checks(source: str) -> list:
	"""Run all PGML checks and return combined results.

	Args:
		source: Full .pgml file content.

	Returns:
		Combined list of all issue dicts from every check.
	"""
	all_issues = []
	all_issues += check_html_whitelist(source)
	all_issues += check_raw_passthrough(source)
	all_issues += check_color_usage(source)
	all_issues += check_variable_scoping(source)
	all_issues += check_structure(source)
	all_issues += check_inline_graders(source)
	all_issues += check_no_beginproblem(source)
	return all_issues

#============================================
def main():
	"""Run assert tests on sample PGML sources."""

	# --- valid PGML source with no issues ---
	valid_source = (
		"DOCUMENT();\n"
		"loadMacros('PGstandard.pl', 'PGML.pl');\n"
		"$answer = Compute('42');\n"
		"BEGIN_PGML\n"
		"What is the answer? [_____]{$answer}\n"
		"END_PGML\n"
		"ENDDOCUMENT();\n"
	)
	valid_issues = run_all_checks(valid_source)
	# filter out variable_scoping warnings (valid source has no 'my' keyword)
	assert len(valid_issues) == 0, f"Expected 0 issues for valid source, got {len(valid_issues)}: {valid_issues}"

	# --- source with deliberate errors ---
	bad_source = (
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
	bad_issues = run_all_checks(bad_source)

	# collect check names from issues
	check_names = [issue["check"] for issue in bad_issues]

	# verify expected checks fired
	assert "no_beginproblem" in check_names, "Should detect TEXT(beginproblem())"
	assert "variable_scoping" in check_names, "Should detect 'my $var'"
	assert "html_whitelist" in check_names, "Should detect blocked HTML tags"
	assert "raw_passthrough" in check_names, "Should detect [$var] without *"
	assert "color_usage" in check_names, "Should detect \\color{}"
	assert "inline_graders" in check_names, "Should detect blank without grader"

	# verify severity values are valid
	for issue in bad_issues:
		assert issue["severity"] in ("error", "warning"), f"Invalid severity: {issue['severity']}"
		assert isinstance(issue["line"], int), f"Line should be int: {issue['line']}"
		assert isinstance(issue["check"], str), f"Check should be str: {issue['check']}"
		assert isinstance(issue["message"], str), f"Message should be str: {issue['message']}"

	# --- test structure errors ---
	no_doc_source = (
		"loadMacros('PGstandard.pl');\n"
		"BEGIN_PGML\n"
		"Hello\n"
		"END_PGML\n"
	)
	struct_issues = check_structure(no_doc_source)
	struct_checks = [i["message"] for i in struct_issues]
	assert any("Missing DOCUMENT()" in m for m in struct_checks), "Should detect missing DOCUMENT()"
	assert any("Missing ENDDOCUMENT()" in m for m in struct_checks), "Should detect missing ENDDOCUMENT()"

	# --- test mismatched PGML blocks ---
	mismatch_source = (
		"DOCUMENT();\n"
		"BEGIN_PGML\n"
		"Hello\n"
		"BEGIN_PGML\n"
		"World\n"
		"END_PGML\n"
		"ENDDOCUMENT();\n"
	)
	mismatch_issues = check_structure(mismatch_source)
	mismatch_msgs = [i["message"] for i in mismatch_issues]
	assert any("Mismatched BEGIN_PGML" in m for m in mismatch_msgs), "Should detect mismatched PGML blocks"

	print("All assert tests passed.")

#============================================
if __name__ == '__main__':
	main()
