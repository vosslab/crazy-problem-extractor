#!/usr/bin/env python3

"""Pytest tests for textbook_clean module."""

# Standard Library
import sys

# local repo modules
import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import textbook_clean


# ============================================================
# normalize_whitespace tests
# ============================================================

#============================================
def test_normalize_whitespace_collapses_spaces() -> None:
	"""Multiple spaces collapse to a single space."""
	result = textbook_clean.normalize_whitespace("hello   world")
	assert result == "hello world"


#============================================
def test_normalize_whitespace_strips_trailing() -> None:
	"""Trailing whitespace is removed from each line."""
	result = textbook_clean.normalize_whitespace("  trailing  ")
	assert result == " trailing"


#============================================
def test_normalize_whitespace_crlf() -> None:
	"""Windows-style line endings are normalized to unix."""
	result = textbook_clean.normalize_whitespace("a\r\nb\rc")
	assert result == "a\nb\nc"


#============================================
def test_normalize_whitespace_preserves_newlines() -> None:
	"""Newlines are not collapsed into spaces."""
	result = textbook_clean.normalize_whitespace("line1  \n  line2")
	assert result == "line1\n line2"


#============================================
def test_normalize_whitespace_empty_string() -> None:
	"""Empty string returns empty string."""
	result = textbook_clean.normalize_whitespace("")
	assert result == ""


#============================================
def test_normalize_whitespace_tabs_collapsed() -> None:
	"""Tab characters collapse to a single space."""
	result = textbook_clean.normalize_whitespace("hello\t\tworld")
	assert result == "hello world"


#============================================
def test_normalize_whitespace_mixed_whitespace() -> None:
	"""Mixed tabs and spaces collapse to a single space."""
	result = textbook_clean.normalize_whitespace("a \t b")
	assert result == "a b"


# ============================================================
# remove_page_headers tests
# ============================================================

#============================================
def test_remove_page_headers_bare_page_numbers() -> None:
	"""Bare 1-4 digit numbers are removed."""
	result = textbook_clean.remove_page_headers(["hello", "123", "world"])
	assert result == ["hello", "world"]


#============================================
def test_remove_page_headers_padded_page_number() -> None:
	"""Page numbers surrounded by whitespace are removed."""
	result = textbook_clean.remove_page_headers(["  42  ", "content"])
	assert result == ["content"]


#============================================
def test_remove_page_headers_intentionally_blank() -> None:
	"""Standard intentionally blank marker is removed."""
	result = textbook_clean.remove_page_headers(
		["This page intentionally blank", "real text"]
	)
	assert result == ["real text"]


#============================================
def test_remove_page_headers_intentionally_blank_with_is_left() -> None:
	"""Variant with 'is left' is also removed."""
	result = textbook_clean.remove_page_headers(
		["this page is left intentionally blank"]
	)
	assert result == []


#============================================
def test_remove_page_headers_blank_lines_removed() -> None:
	"""Empty and whitespace-only lines are removed."""
	result = textbook_clean.remove_page_headers(["", "  ", "data"])
	assert result == ["data"]


#============================================
def test_remove_page_headers_keeps_content_with_numbers() -> None:
	"""Lines that contain numbers along with text are kept."""
	result = textbook_clean.remove_page_headers(["Chapter 12 covers pH"])
	assert result == ["Chapter 12 covers pH"]


#============================================
def test_remove_page_headers_keeps_five_digit_number() -> None:
	"""Numbers with 5+ digits are not treated as page numbers."""
	result = textbook_clean.remove_page_headers(["12345"])
	assert result == ["12345"]


#============================================
def test_remove_page_headers_single_digit() -> None:
	"""Single digit page numbers are removed."""
	result = textbook_clean.remove_page_headers(["5", "content"])
	assert result == ["content"]


#============================================
def test_remove_page_headers_four_digit() -> None:
	"""Four digit page numbers are removed."""
	result = textbook_clean.remove_page_headers(["1234", "content"])
	assert result == ["content"]


#============================================
def test_remove_page_headers_empty_input() -> None:
	"""Empty list returns empty list."""
	result = textbook_clean.remove_page_headers([])
	assert result == []


#============================================
def test_remove_page_headers_all_artifacts() -> None:
	"""Input of only artifacts returns empty list."""
	result = textbook_clean.remove_page_headers(["", "42", "  ", "99"])
	assert result == []


#============================================
def test_remove_page_headers_case_insensitive_blank() -> None:
	"""Intentionally blank marker is case insensitive."""
	result = textbook_clean.remove_page_headers(
		["THIS PAGE INTENTIONALLY BLANK"]
	)
	assert result == []


# ============================================================
# join_split_lines tests
# ============================================================

#============================================
def test_join_split_lines_hyphenated() -> None:
	"""Hyphenated word split across lines is rejoined."""
	result = textbook_clean.join_split_lines(["hydro-", "chloric acid"])
	assert result == ["hydrochloric acid"]


#============================================
def test_join_split_lines_mid_sentence() -> None:
	"""Mid-sentence break followed by lowercase is joined."""
	result = textbook_clean.join_split_lines(
		["The quick brown", "fox jumped"]
	)
	assert result == ["The quick brown fox jumped"]


#============================================
def test_join_split_lines_terminal_period() -> None:
	"""Line ending with period is not joined to the next."""
	result = textbook_clean.join_split_lines(
		["End of sentence.", "Next line"]
	)
	assert result == ["End of sentence.", "Next line"]


#============================================
def test_join_split_lines_terminal_colon() -> None:
	"""Line ending with colon is not joined to the next."""
	result = textbook_clean.join_split_lines(
		["A heading:", "details here"]
	)
	assert result == ["A heading:", "details here"]


#============================================
def test_join_split_lines_empty_list() -> None:
	"""Empty list returns empty list."""
	result = textbook_clean.join_split_lines([])
	assert result == []


#============================================
def test_join_split_lines_single_line() -> None:
	"""Single line is returned unchanged."""
	result = textbook_clean.join_split_lines(["single line"])
	assert result == ["single line"]


#============================================
def test_join_split_lines_hyphen_not_lowercase() -> None:
	"""Hyphenated line is not joined when next line starts uppercase."""
	result = textbook_clean.join_split_lines(["self-", "Aware agent"])
	assert result == ["self-", "Aware agent"]


#============================================
def test_join_split_lines_terminal_question_mark() -> None:
	"""Line ending with question mark is not joined."""
	result = textbook_clean.join_split_lines(
		["Is this correct?", "yes it is"]
	)
	assert result == ["Is this correct?", "yes it is"]


#============================================
def test_join_split_lines_terminal_exclamation() -> None:
	"""Line ending with exclamation mark is not joined."""
	result = textbook_clean.join_split_lines(
		["Watch out!", "the floor is wet"]
	)
	assert result == ["Watch out!", "the floor is wet"]


#============================================
def test_join_split_lines_terminal_semicolon() -> None:
	"""Line ending with semicolon is not joined."""
	result = textbook_clean.join_split_lines(
		["First clause;", "second clause"]
	)
	assert result == ["First clause;", "second clause"]


#============================================
def test_join_split_lines_next_starts_uppercase() -> None:
	"""Mid-sentence break not joined when next line starts uppercase."""
	result = textbook_clean.join_split_lines(
		["The quick brown", "Fox jumped"]
	)
	assert result == ["The quick brown", "Fox jumped"]


#============================================
def test_join_split_lines_multiple_joins() -> None:
	"""Multiple consecutive joinable pairs are handled pairwise."""
	result = textbook_clean.join_split_lines(
		["The quick", "brown fox", "jumped over"]
	)
	# join_split_lines merges pairs in a single pass:
	# "The quick" + "brown fox" merges, consuming both; "jumped over" remains
	assert result == ["The quick brown fox", "jumped over"]


# ============================================================
# clean_text integration tests
# ============================================================

#============================================
def test_clean_text_integration() -> None:
	"""Full pipeline: normalize, remove headers, rejoin splits."""
	raw_input = "The quick   brown\r\nfox jumped over\n 123 \nthe lazy-\ndog.\n"
	cleaned = textbook_clean.clean_text(raw_input)
	# page number 123 should be removed
	assert "123" not in cleaned
	# hyphenated split should be rejoined
	assert "lazydog." in cleaned
	# multiple spaces should be collapsed
	assert "quick brown" in cleaned


#============================================
def test_clean_text_empty_input() -> None:
	"""Empty string returns empty string."""
	result = textbook_clean.clean_text("")
	assert result == ""


#============================================
def test_clean_text_only_artifacts() -> None:
	"""Input of only page artifacts returns empty string."""
	result = textbook_clean.clean_text("42\n\n  99  \n")
	assert result == ""


#============================================
def test_clean_text_preserves_sentences() -> None:
	"""Complete sentences are preserved without merging."""
	raw = "First sentence.\nSecond sentence."
	result = textbook_clean.clean_text(raw)
	assert "First sentence." in result
	assert "Second sentence." in result


#============================================
def test_clean_text_blank_page_marker() -> None:
	"""Intentionally blank page markers are stripped from output."""
	raw = "Real content.\nThis page intentionally blank\nMore content."
	result = textbook_clean.clean_text(raw)
	assert "intentionally" not in result.lower()
	assert "Real content." in result
	assert "More content." in result


#============================================
def test_clean_text_windows_line_endings() -> None:
	"""Windows line endings are normalized in the output."""
	raw = "Line one.\r\nLine two."
	result = textbook_clean.clean_text(raw)
	assert "\r" not in result
	assert "Line one." in result
	assert "Line two." in result
