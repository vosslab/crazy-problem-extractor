#!/usr/bin/env python3

"""Pytest tests for textbook_chapters module.

Tests detect_chapter_boundaries, extract_sections, and extract_key_terms
with both synthetic data and the actual textbook file.
"""

# Standard Library
import os
import pytest

# local repo modules
import git_file_utils
import textbook_chapters
import textbook_clean

REPO_ROOT = git_file_utils.get_repo_root()
TEXTBOOK_PATH = os.path.join(REPO_ROOT, "artifacts", "Tymoczko_3rd_edition.txt")


#============================================
def _load_textbook_lines() -> list:
	"""Load and clean the textbook, returning a list of lines."""
	with open(TEXTBOOK_PATH, "r", encoding="utf-8", errors="replace") as f:
		raw_text = f.read()
	raw_text = textbook_clean.normalize_whitespace(raw_text)
	lines = raw_text.split("\n")
	return lines


# ===== extract_sections tests =====

#============================================
def test_extract_sections_basic() -> None:
	"""Extract three sections from simple chapter lines."""
	sample_lines = [
		"C h a p t e r  1",
		"Biochemistry and the Unity of Life",
		"1.1  Living Systems Require a Limited Variety of Atoms",
		"1.2  There Are Four Major Classes of Biomolecules",
		"Body text here about biochemistry...",
		"1.3  The Central Dogma Describes the Basic Principles",
	]
	sections = textbook_chapters.extract_sections(sample_lines)
	assert len(sections) == 3, f"Expected 3 sections, got {len(sections)}"
	assert sections[0]["section_num"] == "1.1"
	assert "Living Systems" in sections[0]["title"]
	assert sections[1]["section_num"] == "1.2"
	assert sections[2]["section_num"] == "1.3"


#============================================
def test_extract_sections_filters_wrong_chapter() -> None:
	"""Sections from a different chapter number are excluded."""
	sample_lines = [
		"3.1  Proteins Are Built from a Repertoire of 20 Amino Acids",
		"3.2  Side Chains Determine Amino Acid Properties",
		"5.1  This Section Belongs to Chapter 5",
	]
	sections = textbook_chapters.extract_sections(sample_lines)
	# chapter detected as 3, so 5.1 should be excluded
	assert len(sections) == 2
	section_nums = [s["section_num"] for s in sections]
	assert "3.1" in section_nums
	assert "3.2" in section_nums
	assert "5.1" not in section_nums


#============================================
def test_extract_sections_empty_input() -> None:
	"""Empty input returns no sections."""
	sections = textbook_chapters.extract_sections([])
	assert sections == []


#============================================
def test_extract_sections_no_sections() -> None:
	"""Lines with no section patterns return empty list."""
	lines = [
		"Some random text",
		"More text here",
		"No section headings at all",
	]
	sections = textbook_chapters.extract_sections(lines)
	assert sections == []


#============================================
def test_extract_sections_deduplicates() -> None:
	"""Duplicate section numbers are not repeated."""
	sample_lines = [
		"2.1  First Occurrence of Section One",
		"Some body text",
		"2.1  First Occurrence of Section One",
		"2.2  Second Section Title",
	]
	sections = textbook_chapters.extract_sections(sample_lines)
	section_nums = [s["section_num"] for s in sections]
	assert section_nums.count("2.1") == 1
	assert "2.2" in section_nums


#============================================
def test_extract_sections_title_cleanup() -> None:
	"""Whitespace in section titles is normalized."""
	sample_lines = [
		"4.1  Proteins   Have   Multiple   Levels   of   Structure",
	]
	sections = textbook_chapters.extract_sections(sample_lines)
	assert len(sections) == 1
	# extra whitespace should be collapsed
	assert "  " not in sections[0]["title"]


# ===== extract_key_terms tests =====

#============================================
def test_extract_key_terms_basic() -> None:
	"""Parse key terms with page references."""
	term_lines = [
		"kEy TERMS",
		"unity of biochemistry (p. 3)",
		"proteins (p. 5)",
		"nucleic acids (p. 6)",
		"PROBLEMS",
		"1.  E. coli and elephants.",
	]
	terms = textbook_chapters.extract_key_terms(term_lines)
	assert len(terms) == 3, f"Expected 3 terms, got {len(terms)}"
	assert terms[0]["term"] == "unity of biochemistry"
	assert terms[0]["page"] == 3
	assert terms[1]["term"] == "proteins"
	assert terms[1]["page"] == 5
	assert terms[2]["term"] == "nucleic acids"
	assert terms[2]["page"] == 6


#============================================
def test_extract_key_terms_no_heading() -> None:
	"""Lines without a Key Terms heading return empty list."""
	lines = [
		"Some text here",
		"proteins (p. 5)",
		"PROBLEMS",
	]
	terms = textbook_chapters.extract_key_terms(lines)
	assert terms == []


#============================================
def test_extract_key_terms_empty_input() -> None:
	"""Empty input returns no terms."""
	terms = textbook_chapters.extract_key_terms([])
	assert terms == []


#============================================
def test_extract_key_terms_stops_at_problems() -> None:
	"""Parsing stops at the PROBLEMS heading."""
	lines = [
		"Key Terms",
		"enzyme (p. 10)",
		"PROBLEMS",
		"substrate (p. 12)",
	]
	terms = textbook_chapters.extract_key_terms(lines)
	assert len(terms) == 1
	assert terms[0]["term"] == "enzyme"


#============================================
def test_extract_key_terms_stops_at_summary() -> None:
	"""Parsing stops at a Summary heading."""
	lines = [
		"KEY TERMS",
		"catalyst (p. 15)",
		"Summary",
		"active site (p. 20)",
	]
	terms = textbook_chapters.extract_key_terms(lines)
	assert len(terms) == 1
	assert terms[0]["term"] == "catalyst"


#============================================
def test_extract_key_terms_without_page() -> None:
	"""Terms without page references get page=None."""
	lines = [
		"Key Terms",
		"hydrogen bonding",
		"PROBLEMS",
	]
	terms = textbook_chapters.extract_key_terms(lines)
	assert len(terms) == 1
	assert terms[0]["term"] == "hydrogen bonding"
	assert terms[0]["page"] is None


#============================================
def test_extract_key_terms_skips_bare_page_numbers() -> None:
	"""Bare page numbers (page artifacts) are skipped."""
	lines = [
		"Key Terms",
		"42",
		"enzyme (p. 10)",
		"100",
		"PROBLEMS",
	]
	terms = textbook_chapters.extract_key_terms(lines)
	assert len(terms) == 1
	assert terms[0]["term"] == "enzyme"


# ===== detect_chapter_boundaries tests =====

#============================================
def test_detect_chapter_boundaries_empty() -> None:
	"""Empty input returns no boundaries."""
	result = textbook_chapters.detect_chapter_boundaries([])
	assert result == []


#============================================
def test_detect_chapter_boundaries_short_input() -> None:
	"""Short input with no body text returns no boundaries."""
	lines = ["line"] * 100
	result = textbook_chapters.detect_chapter_boundaries(lines)
	assert result == []


#============================================
def test_detect_chapter_boundaries_tuple_structure() -> None:
	"""Each boundary tuple has four elements: start, end, chapter_num, title."""
	# build minimal input that will match at least one chapter
	lines = [""] * 6000
	# insert body start marker
	lines[5001] = "this page left intentionally blank"
	# insert chapter heading
	lines[5010] = "Chapter 1"
	# insert section start
	lines[5020] = "1.1  Living Systems Require a Limited Variety of Atoms"
	# insert answer key marker far enough away
	lines[5500] = "Answers to Problems"
	result = textbook_chapters.detect_chapter_boundaries(lines)
	assert len(result) >= 1
	# check tuple structure
	first = result[0]
	assert len(first) == 4
	start, end, ch_num, title = first
	assert isinstance(start, int)
	assert isinstance(end, int)
	assert isinstance(ch_num, int)
	assert isinstance(title, str)
	assert ch_num == 1
	assert start <= end


#============================================
def test_detect_chapter_boundaries_monotonic_order() -> None:
	"""Chapter boundaries are in monotonically increasing order."""
	lines = [""] * 6000
	lines[5001] = "this page left intentionally blank"
	# place two chapters
	lines[5010] = "Chapter 1"
	lines[5020] = "1.1  Living Systems Require Something"
	lines[5200] = "Chapter 2"
	lines[5210] = "2.1  Water Is the Solvent of Life"
	lines[5900] = "Answers to Problems"
	result = textbook_chapters.detect_chapter_boundaries(lines)
	assert len(result) >= 2
	for i in range(1, len(result)):
		assert result[i][0] > result[i - 1][0], (
			f"Chapter {result[i][2]} start ({result[i][0]}) should be "
			f"after chapter {result[i - 1][2]} start ({result[i - 1][0]})"
		)


# ===== _build_chapter_heading_pattern tests =====

#============================================
def test_chapter_heading_pattern_variants() -> None:
	"""The heading pattern matches varied spacing and case."""
	pattern = textbook_chapters._build_chapter_heading_pattern()
	# normal case
	assert pattern.match("Chapter 1")
	# varied capitalization
	assert pattern.match("ChAp Te r 1")
	# extra spacing between letters
	assert pattern.match("C h a p t e r  2")
	assert pattern.match("ChaP TeR 3")
	# must have a number
	assert pattern.match("Chapter 41")
	# should not match without a number
	assert not pattern.match("Chapter")
	# should not match with extra text
	assert not pattern.match("Chapter 1 Introduction")


# ===== _filter_body_headings tests =====

#============================================
def test_filter_body_headings_removes_clusters() -> None:
	"""Headings clustered close together (section intros) are removed."""
	# simulate section intro page: chapters 1,2,3 within 30 lines
	headings = [
		(100, 1),
		(110, 2),
		(120, 3),
		# body chapter heading (isolated)
		(5000, 1),
	]
	filtered = textbook_chapters._filter_body_headings(headings)
	# the isolated heading should remain
	assert len(filtered) == 1
	assert filtered[0] == (5000, 1)


#============================================
def test_filter_body_headings_empty() -> None:
	"""Empty input returns empty list."""
	result = textbook_chapters._filter_body_headings([])
	assert result == []


# ===== actual textbook integration tests =====

#============================================
@pytest.mark.skipif(
	not os.path.exists(TEXTBOOK_PATH),
	reason="Textbook file not available",
)
def test_textbook_detect_41_chapters() -> None:
	"""detect_chapter_boundaries finds 41 chapters in the actual textbook."""
	lines = _load_textbook_lines()
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	chapter_nums = [b[2] for b in boundaries]
	assert len(boundaries) == 41, (
		f"Expected 41 chapters, got {len(boundaries)}: {chapter_nums}"
	)


#============================================
@pytest.mark.skipif(
	not os.path.exists(TEXTBOOK_PATH),
	reason="Textbook file not available",
)
def test_textbook_chapters_sequential() -> None:
	"""Chapters are numbered 1 through 41 in sequence."""
	lines = _load_textbook_lines()
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	chapter_nums = [b[2] for b in boundaries]
	expected = list(range(1, 42))
	assert chapter_nums == expected, (
		f"Chapters not sequential 1-41: {chapter_nums}"
	)


#============================================
@pytest.mark.skipif(
	not os.path.exists(TEXTBOOK_PATH),
	reason="Textbook file not available",
)
def test_textbook_chapters_have_titles() -> None:
	"""Every detected chapter has a non-empty title."""
	lines = _load_textbook_lines()
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	for start, end, ch_num, title in boundaries:
		assert title, f"Chapter {ch_num} has empty title"


#============================================
@pytest.mark.skipif(
	not os.path.exists(TEXTBOOK_PATH),
	reason="Textbook file not available",
)
def test_textbook_chapter1_sections() -> None:
	"""Chapter 1 has sections starting with 1.1."""
	lines = _load_textbook_lines()
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	# get chapter 1 lines
	ch1 = boundaries[0]
	ch1_lines = lines[ch1[0]:ch1[1] + 1]
	sections = textbook_chapters.extract_sections(ch1_lines)
	assert len(sections) >= 1, "Chapter 1 should have at least one section"
	assert sections[0]["section_num"] == "1.1"


#============================================
@pytest.mark.skipif(
	not os.path.exists(TEXTBOOK_PATH),
	reason="Textbook file not available",
)
def test_textbook_extract_key_terms_nonempty() -> None:
	"""At least some chapters have key terms."""
	lines = _load_textbook_lines()
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	chapters_with_terms = 0
	for start, end, ch_num, title in boundaries:
		ch_lines = lines[start:end + 1]
		terms = textbook_chapters.extract_key_terms(ch_lines)
		if terms:
			chapters_with_terms += 1
	assert chapters_with_terms > 0, "No chapters had key terms extracted"
