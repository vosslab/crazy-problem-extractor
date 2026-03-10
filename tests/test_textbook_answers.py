#!/usr/bin/env python3

"""Pytest tests for textbook_answers module."""

# Standard Library
import os
import sys

# PIP3 modules
import pytest

# local repo modules
import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)
import textbook_answers

TEXTBOOK_PATH = os.path.join(REPO_ROOT, "artifacts", "Tymoczko_3rd_edition.txt")

#============================================
# detect_answer_section_boundaries tests
#============================================

#============================================
def test_boundaries_empty_input():
	"""Empty input returns no boundaries."""
	result = textbook_answers.detect_answer_section_boundaries([])
	assert result == []

#============================================
def test_boundaries_no_answer_section():
	"""Lines without an Answers to Problems header return empty."""
	lines = ["Chapter 1", "Some text", "Chapter 2", "More text"]
	result = textbook_answers.detect_answer_section_boundaries(lines)
	assert result == []

#============================================
def test_boundaries_answer_header_before_halfway():
	"""Answer header in the first half of the file is ignored."""
	# place header at line 10 of a 100-line file (before halfway)
	lines = ["filler"] * 10
	lines.append("Answers to Problems")
	lines.append("Chapter 1")
	lines.append("1.  Answer text.")
	lines += ["filler"] * 10
	result = textbook_answers.detect_answer_section_boundaries(lines)
	assert result == []

#============================================
def test_boundaries_synthetic_two_chapters():
	"""Synthetic input with two chapters produces correct boundaries."""
	# pad the front so the header is past the halfway point
	padding = ["padding"] * 200
	answer_section = [
		"Answers to Problems",
		"Chapter 1",
		"1.  Answer one.",
		"2.  Answer two.",
		"Chapter 2",
		"1.  Answer one ch2.",
		"Index",
	]
	lines = padding + answer_section
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert len(boundaries) == 2
	# check chapter numbers
	assert boundaries[0][2] == 1
	assert boundaries[1][2] == 2
	# first chapter starts at "Chapter 1" line
	assert lines[boundaries[0][0]] == "Chapter 1"
	# first chapter ends before "Chapter 2"
	assert boundaries[0][1] < boundaries[1][0]

#============================================
def test_boundaries_single_chapter():
	"""Synthetic input with one chapter and Index marker."""
	padding = ["padding"] * 200
	answer_section = [
		"Answers to Problems",
		"Chapter 5",
		"1.  Some answer.",
		"",
		"Index",
	]
	lines = padding + answer_section
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert len(boundaries) == 1
	assert boundaries[0][2] == 5

#============================================
def test_boundaries_no_chapters_after_header():
	"""Answer header present but no Chapter N markers returns empty."""
	padding = ["padding"] * 200
	answer_section = [
		"Answers to Problems",
		"1.  Some answer without chapter header.",
		"2.  Another answer.",
	]
	lines = padding + answer_section
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert boundaries == []

#============================================
def test_boundaries_no_index_marker():
	"""Last chapter extends to end of file when no Index marker exists."""
	padding = ["padding"] * 200
	answer_section = [
		"Answers to Problems",
		"Chapter 10",
		"1.  Answer text.",
		"2.  More answer text.",
		"",
	]
	lines = padding + answer_section
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert len(boundaries) == 1
	assert boundaries[0][2] == 10
	# end line should point to the last non-blank line
	end_idx = boundaries[0][1]
	assert lines[end_idx].strip() != ""

#============================================
def test_boundaries_chapter_ordering():
	"""Multiple chapters are returned in file order."""
	padding = ["padding"] * 200
	answer_section = [
		"Answers to Problems",
		"Chapter 3",
		"1.  Answer.",
		"Chapter 7",
		"1.  Answer.",
		"Chapter 12",
		"1.  Answer.",
		"Index",
	]
	lines = padding + answer_section
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert len(boundaries) == 3
	chapter_nums = [b[2] for b in boundaries]
	assert chapter_nums == [3, 7, 12]
	# each start should be strictly increasing
	starts = [b[0] for b in boundaries]
	assert starts == sorted(starts)

#============================================
# extract_answer_key tests
#============================================

#============================================
def test_extract_simple_answers():
	"""Extract numbered answers from simple input."""
	test_lines = [
		"Chapter 3",
		"1.  The answer to question one.",
		"2.  The answer to question two.",
		"3.  The answer to question three.",
	]
	result = textbook_answers.extract_answer_key(test_lines, 3)
	assert len(result) == 3
	assert result[1] == "The answer to question one."
	assert result[2] == "The answer to question two."
	assert result[3] == "The answer to question three."

#============================================
def test_extract_multiline_answer():
	"""Multi-line answers are joined correctly."""
	test_lines = [
		"Chapter 1",
		"1.  First line of answer",
		"continues on second line.",
	]
	result = textbook_answers.extract_answer_key(test_lines, 1)
	assert 1 in result
	assert "continues on second line." in result[1]

#============================================
def test_extract_answer_with_subparts():
	"""Answer with (a), (b), (c) subparts on continuation line."""
	test_lines = [
		"Chapter 2",
		"2.",
		"(a) 8; (b) 7; (c) 1",
	]
	result = textbook_answers.extract_answer_key(test_lines, 2)
	assert 2 in result
	assert "(a) 8; (b) 7; (c) 1" in result[2]

#============================================
def test_extract_skips_page_headers():
	"""Page headers like 'Answers to Problems  C3' are skipped."""
	test_lines = [
		"Chapter 3",
		"1.  Before the page header.",
		"Answers to Problems  C3",
		"2.  After a page header.",
	]
	result = textbook_answers.extract_answer_key(test_lines, 3)
	assert 1 in result
	assert 2 in result
	assert result[2] == "After a page header."

#============================================
def test_extract_skips_reverse_page_headers():
	"""Page headers like 'C42  Answers to Problems' are skipped."""
	test_lines = [
		"Chapter 42",
		"1.  Answer one.",
		"C42  Answers to Problems",
		"2.  Answer two.",
	]
	result = textbook_answers.extract_answer_key(test_lines, 42)
	assert 1 in result
	assert 2 in result

#============================================
def test_extract_empty_input():
	"""Empty answer lines return empty dict."""
	result = textbook_answers.extract_answer_key([], 1)
	assert result == {}

#============================================
def test_extract_blank_lines_within_answer():
	"""Blank lines within an answer are handled."""
	test_lines = [
		"Chapter 1",
		"1.  Part one",
		"",
		"part two after blank",
	]
	result = textbook_answers.extract_answer_key(test_lines, 1)
	assert 1 in result
	assert "part two after blank" in result[1]

#============================================
def test_extract_answer_numbers_are_int_keys():
	"""Answer keys in the dict are integers, not strings."""
	test_lines = [
		"Chapter 1",
		"1.  First.",
		"10.  Tenth.",
	]
	result = textbook_answers.extract_answer_key(test_lines, 1)
	assert isinstance(list(result.keys())[0], int)
	assert 1 in result
	assert 10 in result

#============================================
# _is_page_header tests (via run_tests coverage)
#============================================

#============================================
def test_run_tests_pass():
	"""The module's built-in run_tests should pass without error."""
	textbook_answers.run_tests()

#============================================
# Integration test on actual textbook file
#============================================

#============================================
@pytest.mark.skipif(
	not os.path.isfile(TEXTBOOK_PATH),
	reason="Textbook file not found at artifacts/Tymoczko_3rd_edition.txt",
)
def test_real_textbook_answer_section_detected():
	"""Detect answer section boundaries in the real textbook file."""
	with open(TEXTBOOK_PATH, "r", encoding="utf-8") as f:
		lines = f.readlines()
	# strip newlines for consistency
	lines = [line.rstrip("\n") for line in lines]
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	# the textbook should have answer sections for multiple chapters
	assert len(boundaries) > 0, "No answer section boundaries found in textbook"
	# expect many chapters (textbook has 41 chapters in answer section)
	assert len(boundaries) >= 30, (
		f"Expected at least 30 chapter boundaries, got {len(boundaries)}"
	)
	# all chapter numbers should be positive
	for start, end, chapter_num in boundaries:
		assert chapter_num > 0, f"Invalid chapter number: {chapter_num}"
		assert start < end, (
			f"Chapter {chapter_num}: start ({start}) >= end ({end})"
		)
	# chapter numbers should be unique
	chapter_nums = [b[2] for b in boundaries]
	assert len(chapter_nums) == len(set(chapter_nums)), "Duplicate chapter numbers found"

#============================================
@pytest.mark.skipif(
	not os.path.isfile(TEXTBOOK_PATH),
	reason="Textbook file not found at artifacts/Tymoczko_3rd_edition.txt",
)
def test_real_textbook_extract_chapter_answers():
	"""Extract answers from a chapter in the real textbook."""
	with open(TEXTBOOK_PATH, "r", encoding="utf-8") as f:
		lines = f.readlines()
	lines = [line.rstrip("\n") for line in lines]
	boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	assert len(boundaries) > 0, "No boundaries found"
	# pick the first chapter boundary and extract its answers
	start, end, chapter_num = boundaries[0]
	answer_lines = lines[start:end + 1]
	answers = textbook_answers.extract_answer_key(answer_lines, chapter_num)
	# should have at least a few answers
	assert len(answers) > 0, (
		f"No answers extracted for chapter {chapter_num}"
	)
	# all keys should be positive integers
	for key in answers:
		assert isinstance(key, int)
		assert key > 0
	# answer texts should be non-empty strings
	for key, text in answers.items():
		assert isinstance(text, str)
		assert len(text) > 0, f"Empty answer for problem {key}"
