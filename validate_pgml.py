#!/usr/bin/env python3

"""Validate .pgml files by running structural, style, and macro checks.

Combines checks from pgml_checks and pgml_macros modules, plus
additional validation for ASCII compliance, Context() calls,
loadMacros presence, and PGML_SOLUTION presence.
"""

# Standard Library
import os
import re
import glob
import argparse

# local repo modules
import pgml_checks
import pgml_macros

#============================================
def check_ascii_compliance(source: str) -> list:
	"""Check that source contains only ASCII characters.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts for lines with non-ASCII characters.
	"""
	issues = []
	for line_num, line in enumerate(source.splitlines(), start=1):
		for col, char in enumerate(line, start=1):
			if ord(char) > 127:
				issue = {
					"line": line_num,
					"check": "ascii_compliance",
					"message": f"Non-ASCII character U+{ord(char):04X} at column {col}",
					"severity": "error",
				}
				issues.append(issue)
				# report only the first non-ASCII char per line
				break
	return issues

#============================================
def check_context_call(source: str) -> list:
	"""Check that source contains a Context() call.

	Most PGML files need a Context() call to set the math context.

	Args:
		source: Full .pgml file content.

	Returns:
		List of warning dicts if no Context() call is found.
	"""
	issues = []
	if not re.search(r'\bContext\s*\(', source):
		issue = {
			"line": 1,
			"check": "context_call",
			"message": "No Context() call found; most problems need a math context",
			"severity": "warning",
		}
		issues.append(issue)
	return issues

#============================================
def check_load_macros(source: str) -> list:
	"""Check that source contains a loadMacros() call.

	Args:
		source: Full .pgml file content.

	Returns:
		List of error dicts if no loadMacros() call is found.
	"""
	issues = []
	if not re.search(r'\bloadMacros\s*\(', source):
		issue = {
			"line": 1,
			"check": "load_macros",
			"message": "No loadMacros() call found",
			"severity": "error",
		}
		issues.append(issue)
	return issues

#============================================
def check_solution_present(source: str) -> list:
	"""Check that a PGML_SOLUTION block is present.

	Good practice to include a solution for students.

	Args:
		source: Full .pgml file content.

	Returns:
		List of warning dicts if no PGML_SOLUTION block is found.
	"""
	issues = []
	if not re.search(r'\bBEGIN_PGML_SOLUTION\b', source):
		issue = {
			"line": 1,
			"check": "solution_present",
			"message": "No BEGIN_PGML_SOLUTION block found; consider adding a solution",
			"severity": "warning",
		}
		issues.append(issue)
	return issues

#============================================
def validate_source(source: str) -> list:
	"""Run all validation checks on a single PGML source string.

	Args:
		source: Full .pgml file content.

	Returns:
		Combined list of all issue dicts, sorted by line number.
	"""
	all_issues = []
	# checks from pgml_checks module
	all_issues += pgml_checks.run_all_checks(source)
	# macro-widget pairing from pgml_macros module
	all_issues += pgml_macros.validate_macro_widget_pairing(source)
	# additional local checks
	all_issues += check_ascii_compliance(source)
	all_issues += check_context_call(source)
	all_issues += check_load_macros(source)
	all_issues += check_solution_present(source)
	# sort by line number for readable output
	all_issues.sort(key=lambda i: i["line"])
	return all_issues

#============================================
def validate_file(file_path: str) -> list:
	"""Read and validate a single .pgml file.

	Args:
		file_path: Path to the .pgml file.

	Returns:
		List of issue dicts with 'file' key added.
	"""
	with open(file_path, "r", encoding="utf-8") as f:
		source = f.read()
	issues = validate_source(source)
	# add file path to each issue
	for issue in issues:
		issue["file"] = file_path
	return issues

#============================================
def validate_directory(dir_path: str) -> dict:
	"""Validate all .pgml files in a directory recursively.

	Args:
		dir_path: Path to the directory to scan.

	Returns:
		Dict mapping file_path to list of issues for that file.
	"""
	# find all .pgml files recursively
	search_pattern = os.path.join(dir_path, "**", "*.pgml")
	pgml_files = sorted(glob.glob(search_pattern, recursive=True))

	results = {}
	for pgml_file in pgml_files:
		file_issues = validate_file(pgml_file)
		results[pgml_file] = file_issues
	return results

#============================================
def format_issue(issue: dict) -> str:
	"""Format a single issue dict as a human-readable line.

	Args:
		issue: Issue dict with file, line, check, severity, message keys.

	Returns:
		Formatted string like "path:line [severity] check: message"
	"""
	file_path = issue.get("file", "<unknown>")
	line_num = issue.get("line", 0)
	severity = issue.get("severity", "error").upper()
	check = issue.get("check", "unknown")
	message = issue.get("message", "")
	formatted = f"{file_path}:{line_num} [{severity}] {check}: {message}"
	return formatted

#============================================
def print_results_rich(all_results: dict) -> tuple:
	"""Print validation results using rich for colored output.

	Args:
		all_results: Dict mapping file_path to list of issues.

	Returns:
		Tuple of (error_count, warning_count).
	"""
	import rich.console
	console = rich.console.Console()

	error_count = 0
	warning_count = 0

	for file_path, issues in sorted(all_results.items()):
		if issues:
			console.print(f"\n[bold]{file_path}[/bold]")
		for issue in issues:
			line_num = issue.get("line", 0)
			check = issue.get("check", "unknown")
			message = issue.get("message", "")
			if issue["severity"] == "error":
				error_count += 1
				severity_tag = "[red]ERROR  [/red]"
			else:
				warning_count += 1
				severity_tag = "[yellow]WARNING[/yellow]"
			console.print(f"  {severity_tag} line {line_num:4d}  [{check}] {message}")

	return (error_count, warning_count)

#============================================
def print_results_plain(all_results: dict) -> tuple:
	"""Print validation results as plain text.

	Args:
		all_results: Dict mapping file_path to list of issues.

	Returns:
		Tuple of (error_count, warning_count).
	"""
	error_count = 0
	warning_count = 0

	for file_path, issues in sorted(all_results.items()):
		if issues:
			print(f"\n{file_path}")
		for issue in issues:
			line_num = issue.get("line", 0)
			check = issue.get("check", "unknown")
			severity = issue.get("severity", "error").upper()
			message = issue.get("message", "")
			print(f"  {severity:7s} line {line_num:4d}  [{check}] {message}")
			if issue["severity"] == "error":
				error_count += 1
			else:
				warning_count += 1

	return (error_count, warning_count)

#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Validate .pgml files for common issues"
	)
	parser.add_argument(
		'path',
		help="Path to a .pgml file or directory containing .pgml files",
	)
	args = parser.parse_args()
	return args

#============================================
def main() -> None:
	"""Run PGML validation on files specified by command-line arguments."""
	args = parse_args()
	target_path = args.path

	# validate path exists
	if not os.path.exists(target_path):
		raise FileNotFoundError(f"Path not found: {target_path}")

	# collect results into a dict keyed by file path
	all_results = {}
	if os.path.isfile(target_path):
		file_issues = validate_file(target_path)
		all_results[target_path] = file_issues
	elif os.path.isdir(target_path):
		all_results = validate_directory(target_path)
	else:
		raise FileNotFoundError(f"Path is not a file or directory: {target_path}")

	file_count = len(all_results)
	if file_count == 0:
		print(f"No .pgml files found at: {target_path}")
		return

	# try rich for colored output, fall back to plain text
	use_rich = False
	try:
		import rich.console
		use_rich = True
	except ImportError:
		pass

	if use_rich:
		error_count, warning_count = print_results_rich(all_results)
	else:
		error_count, warning_count = print_results_plain(all_results)

	# print summary line
	summary = f"\n{file_count} file(s) checked, {error_count} error(s), {warning_count} warning(s)"
	if use_rich:
		console = rich.console.Console()
		if error_count > 0:
			console.print(f"[bold red]{summary}[/bold red]")
		elif warning_count > 0:
			console.print(f"[bold yellow]{summary}[/bold yellow]")
		else:
			console.print(f"[bold green]{summary}[/bold green]")
	else:
		print(summary)

	# non-zero exit via exception if errors found
	if error_count > 0:
		raise SystemExit(1)

#============================================
if __name__ == '__main__':
	main()
