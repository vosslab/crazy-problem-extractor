#!/usr/bin/env python3

"""Validate PGML files by sending them to a local renderer and checking for errors."""

# Standard Library
import os
import time
import random
import argparse

# PIP3 modules
import requests

#============================================
def render_pgml(source: str, renderer_url: str) -> dict:
	"""Send PGML source to the renderer API and return the JSON response.

	Args:
		source: the PGML source text to render
		renderer_url: URL of the renderer API endpoint

	Returns:
		dict with the renderer JSON response
	"""
	# sleep to avoid overloading the server per PYTHON_STYLE.md
	time.sleep(random.random())
	# send the PGML source to the renderer
	response = requests.post(
		renderer_url,
		data=source,
		headers={"Content-Type": "text/plain"},
		timeout=30,
	)
	# parse the JSON response
	result = response.json()
	return result

#============================================
def check_render_result(result: dict) -> list:
	"""Analyze a renderer response for errors and warnings.

	Args:
		result: dict from the renderer JSON response

	Returns:
		list of dicts with keys: check, message, severity
	"""
	issues = []
	# check for error_flag in the response
	error_flag = result.get("error_flag")
	if error_flag:
		issue = {
			"check": "error_flag",
			"message": str(error_flag),
			"severity": "error",
		}
		issues.append(issue)
	# check for pg_warn messages
	pg_warn = result.get("pg_warn")
	if pg_warn:
		issue = {
			"check": "pg_warn",
			"message": str(pg_warn),
			"severity": "warning",
		}
		issues.append(issue)
	# check for flags field (alternate error indicator)
	flags = result.get("flags")
	if flags:
		issue = {
			"check": "flags",
			"message": str(flags),
			"severity": "warning",
		}
		issues.append(issue)
	# check for internal diagnostics
	debug = result.get("debug")
	if debug:
		issue = {
			"check": "debug",
			"message": str(debug),
			"severity": "info",
		}
		issues.append(issue)
	# check for problem_result errors
	problem_result = result.get("problem_result", {})
	if isinstance(problem_result, dict):
		result_errors = problem_result.get("errors")
		if result_errors:
			issue = {
				"check": "problem_result_errors",
				"message": str(result_errors),
				"severity": "error",
			}
			issues.append(issue)
	# check for answers_submitted errors
	answers = result.get("answers", {})
	if isinstance(answers, dict):
		for key, value in answers.items():
			if isinstance(value, dict) and value.get("error_message"):
				issue = {
					"check": f"answer_error:{key}",
					"message": str(value["error_message"]),
					"severity": "error",
				}
				issues.append(issue)
	return issues

#============================================
def validate_file(file_path: str, renderer_url: str) -> list:
	"""Validate a single PGML file by rendering it and checking for issues.

	Args:
		file_path: path to the .pgml file
		renderer_url: URL of the renderer API endpoint

	Returns:
		list of issue dicts from check_render_result
	"""
	# read the PGML source file
	with open(file_path, "r") as f:
		source = f.read()
	# send to renderer and get the result
	result = render_pgml(source, renderer_url)
	# check the result for errors and warnings
	issues = check_render_result(result)
	return issues

#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		argparse.Namespace with parsed arguments
	"""
	parser = argparse.ArgumentParser(
		description="Validate PGML files by sending them to a local renderer"
	)
	parser.add_argument(
		'-i', '--input', dest='input_path', required=True,
		help="Path to a .pgml file or directory containing .pgml files",
	)
	parser.add_argument(
		'-u', '--url', dest='renderer_url',
		default="http://localhost:3000/render-api",
		help="Renderer API URL (default: http://localhost:3000/render-api)",
	)
	args = parser.parse_args()
	return args

#============================================
def main():
	"""Entry point: validate PGML files and print results."""
	args = parse_args()
	input_path = args.input_path
	renderer_url = args.renderer_url
	# collect list of pgml files to validate
	pgml_files = []
	if os.path.isdir(input_path):
		# find all .pgml files in the directory
		for filename in sorted(os.listdir(input_path)):
			if filename.endswith(".pgml"):
				full_path = os.path.join(input_path, filename)
				pgml_files.append(full_path)
		if not pgml_files:
			print(f"No .pgml files found in {input_path}")
			return
	elif os.path.isfile(input_path):
		pgml_files.append(input_path)
	else:
		print(f"Input path not found: {input_path}")
		return
	print(f"Validating {len(pgml_files)} PGML file(s) against {renderer_url}")
	print()
	# track total issues
	total_issues = 0
	for file_path in pgml_files:
		print(f"--- {file_path} ---")
		issues = validate_file(file_path, renderer_url)
		if not issues:
			print("  OK: no issues found")
		else:
			for issue in issues:
				severity_tag = issue["severity"].upper()
				check_name = issue["check"]
				message = issue["message"]
				print(f"  [{severity_tag}] {check_name}: {message}")
				total_issues += 1
		print()
	# print summary
	file_count = len(pgml_files)
	print(f"Summary: {total_issues} issue(s) in {file_count} file(s)")

#============================================
if __name__ == '__main__':
	main()
