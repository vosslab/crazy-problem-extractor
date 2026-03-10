#!/usr/bin/env python3

"""Textbook text cleaning utilities.

Normalizes whitespace, removes page headers/footers, and rejoins
lines that were split across page boundaries.
"""

# Standard Library
import re

#============================================
def normalize_whitespace(text: str) -> str:
	"""Normalize whitespace in text.

	Args:
		text: raw text string to normalize.

	Returns:
		Text with collapsed spaces, stripped trailing whitespace,
		and normalized line endings.
	"""
	# normalize line endings to unix style
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	# collapse multiple spaces (not newlines) to a single space
	text = re.sub(r"[^\S\n]+", " ", text)
	# strip trailing whitespace from each line
	lines = [line.rstrip() for line in text.split("\n")]
	result = "\n".join(lines)
	return result

#============================================
def remove_page_headers(lines: list) -> list:
	"""Strip page header and footer artifacts from lines.

	Removes lines that are bare page numbers (1-4 digit numbers alone
	on a line), 'this page left intentionally blank' markers, and
	lines that are only whitespace.

	Args:
		lines: list of text lines to filter.

	Returns:
		Filtered list with header/footer artifacts removed.
	"""
	cleaned = []
	# pattern for bare page numbers: optional whitespace, 1-4 digits, optional whitespace
	page_number_pattern = re.compile(r"^\s*\d{1,4}\s*$")
	# pattern for intentionally blank page markers
	blank_page_pattern = re.compile(
		r"^\s*this\s+page\s+(is\s+)?(left\s+)?intentionally\s+blank\s*$",
		re.IGNORECASE,
	)
	for line in lines:
		# skip lines that are only whitespace
		if line.strip() == "":
			continue
		# skip bare page numbers
		if page_number_pattern.match(line):
			continue
		# skip intentionally blank page markers
		if blank_page_pattern.match(line):
			continue
		cleaned.append(line)
	return cleaned

#============================================
def join_split_lines(lines: list) -> list:
	"""Rejoin lines broken by page breaks or mid-sentence splits.

	Handles two patterns:
	- Hyphenated word splits: 'word-' at end of line joined with start of next line
	- Mid-sentence breaks: line ends without terminal punctuation and next line
	  starts with a lowercase letter

	Args:
		lines: list of text lines to rejoin.

	Returns:
		List of lines with broken lines merged.
	"""
	if not lines:
		return []
	# terminal punctuation that signals end of a sentence or heading
	terminal_chars = ".!?:;"
	joined = []
	i = 0
	while i < len(lines):
		current = lines[i]
		# check if we can peek at the next line
		if i + 1 < len(lines):
			next_line = lines[i + 1]
			next_stripped = next_line.lstrip()
			# case 1: hyphenated word split at line boundary
			if current.rstrip().endswith("-") and next_stripped and next_stripped[0].islower():
				# remove the trailing hyphen and join with the next line
				merged = current.rstrip()[:-1] + next_stripped
				joined.append(merged)
				# skip the next line since we merged it
				i += 2
				continue
			# case 2: line ends mid-sentence and next line continues with lowercase
			current_stripped = current.rstrip()
			if (current_stripped
				and current_stripped[-1] not in terminal_chars
				and next_stripped
				and next_stripped[0].islower()):
				# join with a space
				merged = current_stripped + " " + next_stripped
				joined.append(merged)
				i += 2
				continue
		# no merging needed
		joined.append(current)
		i += 1
	return joined

#============================================
def clean_text(raw: str) -> str:
	"""Clean raw textbook text by normalizing, filtering, and rejoining.

	This is the main entry point. It normalizes whitespace, removes
	page header/footer artifacts, and rejoins lines split across pages.

	Args:
		raw: raw text extracted from a textbook.

	Returns:
		Cleaned text string.
	"""
	# step 1: normalize whitespace
	text = normalize_whitespace(raw)
	# step 2: split into lines and remove page artifacts
	lines = text.split("\n")
	lines = remove_page_headers(lines)
	# step 3: rejoin lines broken across page boundaries
	lines = join_split_lines(lines)
	# reassemble into a single string
	result = "\n".join(lines)
	return result

#============================================
def run_tests() -> None:
	"""Run assert tests for the cleaning functions."""
	# -- normalize_whitespace tests --
	assert normalize_whitespace("hello   world") == "hello world"
	assert normalize_whitespace("line1  \n  line2") == "line1\n line2"
	assert normalize_whitespace("a\r\nb\rc") == "a\nb\nc"
	assert normalize_whitespace("  trailing  ") == " trailing"

	# -- remove_page_headers tests --
	assert remove_page_headers(["hello", "123", "world"]) == ["hello", "world"]
	assert remove_page_headers(["  42  ", "content"]) == ["content"]
	assert remove_page_headers(["This page intentionally blank", "real text"]) == ["real text"]
	assert remove_page_headers(["this page is left intentionally blank"]) == []
	assert remove_page_headers(["", "  ", "data"]) == ["data"]
	# real content with numbers should stay
	assert remove_page_headers(["Chapter 12 covers pH"]) == ["Chapter 12 covers pH"]
	assert remove_page_headers(["12345"]) == ["12345"]

	# -- join_split_lines tests --
	assert join_split_lines(["hydro-", "chloric acid"]) == ["hydrochloric acid"]
	assert join_split_lines(["The quick brown", "fox jumped"]) == ["The quick brown fox jumped"]
	assert join_split_lines(["End of sentence.", "Next line"]) == ["End of sentence.", "Next line"]
	assert join_split_lines(["A heading:", "details here"]) == ["A heading:", "details here"]
	assert join_split_lines([]) == []
	assert join_split_lines(["single line"]) == ["single line"]

	# -- clean_text integration test --
	raw_input = "The quick   brown\r\nfox jumped over\n 123 \nthe lazy-\ndog.\n"
	cleaned = clean_text(raw_input)
	assert "123" not in cleaned
	assert "lazydog." in cleaned
	assert "quick brown" in cleaned

	print("All tests passed.")

#============================================
def main() -> None:
	"""Main entry point for textbook_clean module."""
	run_tests()

#============================================
if __name__ == "__main__":
	main()
