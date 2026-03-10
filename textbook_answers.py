#!/usr/bin/env python3

"""Parse answer key sections from biochemistry textbook text files.

Detects chapter-level answer boundaries in 'Answers to Problems' sections
and extracts numbered answers for each chapter.
"""

# Standard Library
import re

# local repo modules
import textbook_clean

#============================================
def detect_answer_section_boundaries(lines: list) -> list:
	"""Find answer block boundaries for each chapter in the answer key.

	Scans lines for the 'Answers to Problems' section, then uses 'Chapter N'
	markers within that section to identify per-chapter answer blocks.

	The textbook contains page headers like 'Answers to Problems  C3' or
	'C42  Answers to Problems' at page boundaries. These are treated as
	noise and skipped when determining chapter boundaries.

	Args:
		lines: list of text lines from the full textbook file.

	Returns:
		List of tuples (start_line, end_line, chapter_num) where start_line
		and end_line are 0-based indices into the lines list, and chapter_num
		is the integer chapter number.
	"""
	# pattern for the main "Answers to Problems" section header (standalone)
	main_header_pattern = re.compile(r"^\s*Answers to Problems\s*$")
	# pattern for "Chapter N" lines that start a chapter's answers
	chapter_pattern = re.compile(r"^\s*Chapter\s+(\d+)\s*$")
	# step 1: find the main "Answers to Problems" section start
	section_start = None
	for i, line in enumerate(lines):
		if main_header_pattern.match(line):
			# verify this is in the back of the book (past the halfway point)
			if i > len(lines) // 2:
				section_start = i
				break
	if section_start is None:
		return []

	# step 2: find "Chapter N" markers within the answer section
	chapter_starts = []
	for i in range(section_start, len(lines)):
		match = chapter_pattern.match(lines[i])
		if match:
			chapter_num = int(match.group(1))
			chapter_starts.append((i, chapter_num))

	if not chapter_starts:
		return []

	# step 3: build boundary tuples for each chapter
	boundaries = []
	for idx in range(len(chapter_starts)):
		start_line = chapter_starts[idx][0]
		chapter_num = chapter_starts[idx][1]
		# end line is the line before the next chapter starts, or end of section
		if idx + 1 < len(chapter_starts):
			end_line = chapter_starts[idx + 1][0] - 1
		else:
			# last chapter: scan forward to find end of answer section
			end_line = _find_section_end(lines, start_line)
		boundaries.append((start_line, end_line, chapter_num))

	return boundaries

#============================================
def _find_section_end(lines: list, start: int) -> int:
	"""Find the end of the answer section after the last chapter.

	Scans forward from start looking for the 'Index' heading or end of file.

	Args:
		lines: list of text lines from the full textbook file.
		start: line index to start scanning from.

	Returns:
		0-based line index of the last answer line.
	"""
	index_pattern = re.compile(r"^\s*Index\s*$")
	for i in range(start, len(lines)):
		if index_pattern.match(lines[i]):
			# back up past any blank lines before 'Index'
			end = i - 1
			while end > start and lines[end].strip() == "":
				end -= 1
			return end
	# if no Index found, return the last non-blank line
	end = len(lines) - 1
	while end > start and lines[end].strip() == "":
		end -= 1
	return end

#============================================
def _is_page_header(line: str) -> bool:
	"""Check if a line is an 'Answers to Problems' page header.

	Args:
		line: text line to check.

	Returns:
		True if the line is a page header like 'Answers to Problems  C3'
		or 'C42  Answers to Problems'.
	"""
	pattern = re.compile(
		r"^\s*(Answers to Problems\s+C\d+|C\d+\s+Answers to Problems)\s*$"
	)
	is_header = bool(pattern.match(line))
	return is_header

#============================================
def extract_answer_key(answer_lines: list, chapter_num: int) -> dict:
	"""Parse numbered answers from a chapter's answer section.

	Processes lines from a single chapter's answer block and extracts
	each numbered answer. Handles multi-line answers including chemical
	formula diagrams spread across lines.

	Args:
		answer_lines: list of text lines for one chapter's answer section.
		chapter_num: integer chapter number (for context/logging).

	Returns:
		Dict mapping problem number (int) to answer text (str).
	"""
	# pattern for the start of a numbered answer: "7." or "7.  text..."
	answer_start_pattern = re.compile(r"^(\d+)\.\s*(.*)")
	answers = {}
	current_number = None
	current_text_parts = []

	for line in answer_lines:
		stripped = line.strip()
		# skip blank lines within an answer (preserve them as separators in text)
		if stripped == "":
			if current_number is not None:
				# blank line within an answer block (chemical formulas, etc.)
				current_text_parts.append("")
			continue
		# skip page headers
		if _is_page_header(line):
			continue
		# skip "Chapter N" lines
		if re.match(r"^\s*Chapter\s+\d+\s*$", line):
			continue

		# check for a new numbered answer
		match = answer_start_pattern.match(stripped)
		if match:
			# save the previous answer if any
			if current_number is not None:
				answer_text = _join_answer_parts(current_text_parts)
				answers[current_number] = answer_text
			# start new answer
			current_number = int(match.group(1))
			first_line_text = match.group(2).strip()
			current_text_parts = []
			if first_line_text:
				current_text_parts.append(first_line_text)
		elif current_number is not None:
			# continuation of the current answer
			current_text_parts.append(stripped)

	# save the last answer
	if current_number is not None:
		answer_text = _join_answer_parts(current_text_parts)
		answers[current_number] = answer_text

	return answers

#============================================
def _join_answer_parts(parts: list) -> str:
	"""Join collected answer text parts into a single string.

	Preserves blank-line separators (for chemical formulas) while
	collapsing regular text continuation into flowing prose.

	Args:
		parts: list of text fragments for a single answer.

	Returns:
		Joined answer text string.
	"""
	# strip trailing empty parts
	while parts and parts[-1] == "":
		parts.pop()
	if not parts:
		return ""
	# join parts and normalize internal whitespace
	raw = "\n".join(parts)
	result = textbook_clean.normalize_whitespace(raw)
	return result

#============================================
def run_tests() -> None:
	"""Run assert-based tests for answer parsing functions."""
	# -- _is_page_header tests --
	assert _is_page_header("Answers to Problems  C3") is True
	assert _is_page_header("C42  Answers to Problems") is True
	assert _is_page_header("Answers to Problems") is False
	assert _is_page_header("Chapter 3") is False
	assert _is_page_header("7.  Some answer text") is False

	# -- _join_answer_parts tests --
	assert _join_answer_parts(["hello", "world"]) == "hello\nworld"
	assert _join_answer_parts([]) == ""
	assert _join_answer_parts(["text", "", ""]) == "text"

	# -- extract_answer_key with simple input --
	test_lines = [
		"Chapter 3",
		"1.  The answer to question one.",
		"2.",
		"(a) 8; (b) 7; (c) 1",
		"3.  Multi-line answer that",
		"continues on the next line.",
		"Answers to Problems  C3",
		"4.  After a page header.",
	]
	result = extract_answer_key(test_lines, 3)
	assert 1 in result
	assert result[1] == "The answer to question one."
	assert 2 in result
	assert "(a) 8; (b) 7; (c) 1" in result[2]
	assert 3 in result
	assert "continues on the next line." in result[3]
	assert 4 in result
	assert result[4] == "After a page header."

	# -- detect_answer_section_boundaries with synthetic input --
	fake_lines = ["filler"] * 100
	fake_lines.append("Answers to Problems")
	fake_lines.append("Chapter 1")
	fake_lines.append("1.  Answer one.")
	fake_lines.append("Chapter 2")
	fake_lines.append("1.  Answer one ch2.")
	fake_lines.append("Index")
	# need to be past the halfway point, so pad the front
	padded = ["padding"] * 200 + fake_lines
	boundaries = detect_answer_section_boundaries(padded)
	assert len(boundaries) == 2
	assert boundaries[0][2] == 1
	assert boundaries[1][2] == 2

	print("All tests passed.")

#============================================
def main() -> None:
	"""Main entry point for textbook_answers module."""
	run_tests()

#============================================
if __name__ == "__main__":
	main()
