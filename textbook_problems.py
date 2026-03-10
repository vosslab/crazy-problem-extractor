#!/usr/bin/env python3

"""Extract numbered problems from textbook chapter text.

Parses PROBLEMS, Challenge Problems, and Data Interpretation Problems
sections from chapter lines extracted from the Tymoczko textbook.
"""

# Standard Library
import re

# pattern to match a numbered problem start like "1.  Some title."
# handles both normal "1.  Text" and split lines where number is alone
PROBLEM_NUMBER_PATTERN = re.compile(r"^(\d+)\.\s+(.*)$")

# section headings that terminate a problem block
SECTION_TERMINATORS = [
	"Challenge Problems",
	"Challenge Problem",
	"Data Interpretation Problems",
	"Data Interpretation Problem",
	"Selected Readings",
	"Answers to",
]

# pattern for chapter or section headers that also terminate problem blocks
CHAPTER_HEADER_PATTERN = re.compile(
	r"^(C\s*h\s*a\s*p\s*t?\s*e\s*r|S\s*e\s*C\s*t?\s*I\s*o?\s*N)\s+\d",
	re.IGNORECASE,
)

#============================================
def _is_section_terminator(line: str) -> bool:
	"""Check if a line is a section heading that terminates problem parsing.

	Args:
		line: text line to check.

	Returns:
		True if the line is a section terminator heading.
	"""
	stripped = line.strip()
	# check against known heading strings
	for heading in SECTION_TERMINATORS:
		if stripped.startswith(heading):
			return True
	# check for chapter/section header pattern
	if CHAPTER_HEADER_PATTERN.match(stripped):
		return True
	# check for bare "PROBLEMS" heading that starts a new chapter's problems
	if stripped == "PROBLEMS":
		return True
	return False

#============================================
def _parse_problems_from_lines(lines: list, start_idx: int) -> list:
	"""Parse numbered problems starting from a given index in lines.

	Reads consecutive numbered problems until a section terminator
	or the end of the lines list is reached. Problems are multi-line
	and end when the next numbered problem starts or a section heading
	appears.

	Args:
		lines: list of all chapter lines.
		start_idx: index to start scanning for numbered problems.

	Returns:
		List of dicts with keys 'number' (int) and 'text' (str).
	"""
	problems = []
	current_number = None
	current_lines = []
	idx = start_idx

	while idx < len(lines):
		line = lines[idx]
		stripped = line.strip()

		# stop at section terminators
		if _is_section_terminator(stripped):
			break

		# check if this line starts a new numbered problem
		match = PROBLEM_NUMBER_PATTERN.match(stripped)
		if match:
			# save previous problem if one exists
			if current_number is not None:
				problem_text = " ".join(current_lines)
				# collapse multiple spaces
				problem_text = re.sub(r"\s+", " ", problem_text).strip()
				problems.append({
					"number": current_number,
					"text": problem_text,
				})
			current_number = int(match.group(1))
			# start collecting text for this problem
			remainder = match.group(2).strip()
			current_lines = [remainder] if remainder else []
			idx += 1
			continue

		# skip blank lines but do not terminate the problem
		if not stripped:
			idx += 1
			continue

		# accumulate continuation lines for the current problem
		if current_number is not None:
			current_lines.append(stripped)

		idx += 1

	# save the last problem if pending
	if current_number is not None:
		problem_text = " ".join(current_lines)
		problem_text = re.sub(r"\s+", " ", problem_text).strip()
		problems.append({
			"number": current_number,
			"text": problem_text,
		})

	return problems

#============================================
def _find_heading_index(chapter_lines: list, headings: list) -> int:
	"""Find the line index of a section heading in chapter lines.

	Args:
		chapter_lines: list of text lines from a chapter.
		headings: list of heading strings to search for (exact match).

	Returns:
		Index of the first matching heading, or -1 if not found.
	"""
	for idx, line in enumerate(chapter_lines):
		stripped = line.strip()
		for heading in headings:
			if stripped == heading:
				return idx
	return -1

#============================================
def extract_problems(chapter_lines: list) -> list:
	"""Extract numbered problems from the PROBLEMS section of a chapter.

	Looks for a line that is exactly "PROBLEMS" and then parses
	numbered entries like "1.  Title. Question text..." until a
	section terminator is reached.

	Args:
		chapter_lines: list of text lines from a single chapter.

	Returns:
		List of dicts with keys 'number' (int) and 'text' (str).
	"""
	heading_idx = _find_heading_index(chapter_lines, ["PROBLEMS"])
	if heading_idx < 0:
		return []
	# start parsing from the line after the heading
	problems = _parse_problems_from_lines(chapter_lines, heading_idx + 1)
	return problems

#============================================
def extract_challenge_problems(chapter_lines: list) -> list:
	"""Extract challenge problems from a chapter.

	Looks for "Challenge Problems" or "Challenge Problem" heading
	and parses the numbered entries that follow.

	Args:
		chapter_lines: list of text lines from a single chapter.

	Returns:
		List of dicts with keys 'number' (int) and 'text' (str).
	"""
	heading_idx = _find_heading_index(
		chapter_lines,
		["Challenge Problems", "Challenge Problem"],
	)
	if heading_idx < 0:
		return []
	problems = _parse_problems_from_lines(chapter_lines, heading_idx + 1)
	return problems

#============================================
def extract_data_interpretation_problems(chapter_lines: list) -> list:
	"""Extract data interpretation problems from a chapter.

	Looks for "Data Interpretation Problems" or "Data Interpretation
	Problem" heading and parses the numbered entries that follow.

	Args:
		chapter_lines: list of text lines from a single chapter.

	Returns:
		List of dicts with keys 'number' (int) and 'text' (str).
	"""
	heading_idx = _find_heading_index(
		chapter_lines,
		["Data Interpretation Problems", "Data Interpretation Problem"],
	)
	if heading_idx < 0:
		return []
	problems = _parse_problems_from_lines(chapter_lines, heading_idx + 1)
	return problems

#============================================
def run_tests() -> None:
	"""Run basic assert tests for the extraction functions."""
	# test basic problem extraction
	sample_lines = [
		"PROBLEMS",
		"",
		"1.  First problem. What is the answer?",
		"",
		"2.  Second problem. Describe the thing",
		"that continues on this line.",
		"",
		"Challenge Problems",
		"3.  Hard one. Explain why.",
		"",
		"Selected Readings for this chapter",
	]
	problems = extract_problems(sample_lines)
	assert len(problems) == 2, f"Expected 2 problems, got {len(problems)}"
	assert problems[0]["number"] == 1
	assert "First problem" in problems[0]["text"]
	assert problems[1]["number"] == 2
	assert "continues on this line" in problems[1]["text"]

	# test challenge problem extraction
	challenge = extract_challenge_problems(sample_lines)
	assert len(challenge) == 1
	assert challenge[0]["number"] == 3
	assert "Hard one" in challenge[0]["text"]

	# test data interpretation extraction
	di_lines = [
		"Data Interpretation Problems",
		"",
		"5.  Graph reading. Look at the graph.",
		"What does it show?",
		"",
		"Selected Readings for this chapter",
	]
	di_problems = extract_data_interpretation_problems(di_lines)
	assert len(di_problems) == 1
	assert di_problems[0]["number"] == 5

	# test singular heading variant
	di_lines_singular = [
		"Data Interpretation Problem",
		"",
		"10.  Single DI problem. Answer this.",
		"",
	]
	di_singular = extract_data_interpretation_problems(di_lines_singular)
	assert len(di_singular) == 1
	assert di_singular[0]["number"] == 10

	# test empty input
	assert extract_problems([]) == []
	assert extract_challenge_problems([]) == []
	assert extract_data_interpretation_problems([]) == []

	# test no matching heading
	assert extract_problems(["Some random text", "No heading here"]) == []

	print("All tests passed.")

#============================================
def main() -> None:
	"""Main entry point for textbook_problems module."""
	run_tests()

#============================================
if __name__ == "__main__":
	main()
