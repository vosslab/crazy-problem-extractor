#!/usr/bin/env python3

"""Detect chapter boundaries, sections, and key terms in the textbook.

Parses the Tymoczko 3rd edition biochemistry textbook to identify
chapter start/end lines, numbered sections, and key terms with page
references.
"""

# Standard Library
import re

# local repo modules
import textbook_clean

# minimum line index to skip the table of contents and front matter
BODY_START_MIN = 5000

#============================================
def _find_body_start(lines: list) -> int:
	"""Find where the body text begins, after front matter.

	Looks for the 'this page left intentionally blank' marker
	that precedes Section 1 of the body text.

	Args:
		lines: list of text lines from the textbook file.

	Returns:
		Line index where body text starts.
	"""
	for i in range(BODY_START_MIN, len(lines)):
		if re.search(r'this\s+page\s+(left\s+)?intentionally\s+blank', lines[i], re.IGNORECASE):
			return i + 1
	# fallback: return a reasonable default
	return BODY_START_MIN

#============================================
def _find_answer_key_start(lines: list, body_start: int) -> int:
	"""Find where the answer key section begins.

	The answer key starts with 'Answers to Problems' followed by
	sequential 'Chapter N' headings.

	Args:
		lines: list of text lines from the textbook file.
		body_start: index where body text starts.

	Returns:
		Line index where the answer key begins.
	"""
	for i in range(body_start, len(lines)):
		stripped = lines[i].strip()
		if stripped == "Answers to Problems":
			return i
	# fallback: return end of file
	return len(lines)

#============================================
def _build_chapter_heading_pattern() -> re.Pattern:
	"""Build a regex that matches chapter headings with varied spacing and case.

	The textbook uses inconsistent capitalization and spacing for chapter
	headings, e.g. 'ChAp Te r 1', 'C h a p t e r  2', 'ChaP TeR 3'.
	This pattern matches all variants.

	Returns:
		Compiled regex pattern with a capture group for the chapter number.
	"""
	# match c-h-a-p-t-e-r with optional spaces/tabs between each letter
	pattern = r'^[Cc]\s*[Hh]\s*[Aa]\s*[Pp]\s*[Tt]\s*[Ee]\s*[Rr]\s+(\d+)\s*$'
	return re.compile(pattern)

#============================================
def _find_first_section_lines(lines: list, body_start: int, body_end: int) -> dict:
	"""Find the first N.1 section heading for each chapter in the body text.

	Looks for patterns like '1.1  Living Systems Require...' to locate
	where each chapter's content begins.

	Args:
		lines: list of text lines from the textbook file.
		body_start: index where body text starts.
		body_end: index where body text ends (answer key start).

	Returns:
		Dict mapping chapter number to line index of first section.
	"""
	section_starts = {}
	# pattern matches "N.1  Title" where N is the chapter number and title starts uppercase
	section_pattern = re.compile(r'^(\d+)\.1\s+[A-Z]')
	for i in range(body_start, body_end):
		stripped = lines[i].strip()
		m = section_pattern.match(stripped)
		if m:
			ch_num = int(m.group(1))
			# only record chapters 1-41 and only the first occurrence
			if 1 <= ch_num <= 41 and ch_num not in section_starts:
				section_starts[ch_num] = i
	return section_starts

#============================================
def _find_chapter_headings(lines: list, body_start: int, body_end: int) -> list:
	"""Find all chapter heading lines in the body text.

	Args:
		lines: list of text lines from the textbook file.
		body_start: index where body text starts.
		body_end: index where body text ends.

	Returns:
		List of (line_index, chapter_number) tuples.
	"""
	heading_pattern = _build_chapter_heading_pattern()
	matches = []
	for i in range(body_start, body_end):
		stripped = lines[i].strip()
		m = heading_pattern.match(stripped)
		if m:
			ch_num = int(m.group(1))
			if 1 <= ch_num <= 41:
				matches.append((i, ch_num))
	return matches

#============================================
def _filter_body_headings(all_headings: list) -> list:
	"""Filter out section intro headings, keeping only body chapter starts.

	Section intro pages list multiple chapters close together (within
	~50 lines). Body chapter starts appear in isolation, far from other
	chapter headings.

	Args:
		all_headings: list of (line_index, chapter_number) tuples.

	Returns:
		Filtered list keeping only isolated (body) chapter headings.
	"""
	if not all_headings:
		return []
	# for each heading, check if a DIFFERENT chapter heading is within 50 lines
	cluster_distance = 50
	body_headings = []
	for i, (line_idx, ch_num) in enumerate(all_headings):
		is_clustered = False
		for j, (other_idx, other_num) in enumerate(all_headings):
			if i == j:
				continue
			# different chapter number within cluster distance
			if other_num != ch_num and abs(other_idx - line_idx) < cluster_distance:
				is_clustered = True
				break
		if not is_clustered:
			body_headings.append((line_idx, ch_num))
	return body_headings

#============================================
def _extract_title_after_heading(lines: list, heading_idx: int) -> str:
	"""Extract the chapter title from lines following a chapter heading.

	The title typically spans 1-3 lines immediately after the heading.

	Args:
		lines: list of text lines from the textbook file.
		heading_idx: index of the chapter heading line.

	Returns:
		Extracted chapter title string.
	"""
	title_parts = []
	# look at the next few lines for the title
	for j in range(heading_idx + 1, min(heading_idx + 6, len(lines))):
		stripped = lines[j].strip()
		# stop at empty lines, section patterns, or other chapter headings
		if not stripped:
			if title_parts:
				break
			continue
		# stop if we hit a section number pattern like "1.1 ..."
		if re.match(r'^\d+\.\d+\s', stripped):
			break
		# stop if we hit another chapter heading
		if re.match(r'^[Cc]\s*[Hh]\s*[Aa]\s*[Pp]', stripped):
			break
		# stop if we hit a bare page number
		if re.match(r'^\d{1,4}$', stripped):
			continue
		title_parts.append(stripped)
	title = " ".join(title_parts)
	# clean up extra whitespace and tab characters
	title = re.sub(r'\s+', ' ', title).strip()
	return title

#============================================
def _extract_title_from_toc(lines: list, chapter_num: int) -> str:
	"""Extract chapter title from the table of contents as a fallback.

	Searches lines 1900-2100 for 'Chapter N  Title' patterns.

	Args:
		lines: list of text lines from the textbook file.
		chapter_num: chapter number to find.

	Returns:
		Chapter title string, or empty string if not found.
	"""
	toc_pattern = re.compile(
		rf'^Chapter\s+{chapter_num}\s+(.+)',
		re.IGNORECASE,
	)
	# search the TOC region
	start = min(1900, len(lines))
	end = min(2100, len(lines))
	for i in range(start, end):
		m = toc_pattern.match(lines[i].strip())
		if m:
			title = m.group(1).strip()
			# remove trailing page numbers
			title = re.sub(r'\s+\d+\s*$', '', title)
			return title
	return ""

#============================================
def detect_chapter_boundaries(lines: list) -> list:
	"""Detect chapter boundaries in the textbook body text.

	Scans lines for chapter heading patterns and section start markers,
	skipping the table of contents and front matter. Identifies the
	start line, end line, chapter number, and title for each chapter.

	Args:
		lines: list of text lines from the textbook file.

	Returns:
		List of tuples (start_line, end_line, chapter_num, title)
		where start_line and end_line are 0-based indices into lines.
	"""
	body_start = _find_body_start(lines)
	body_end = _find_answer_key_start(lines, body_start)

	# find all chapter headings, filter to body-only, and find section lines
	all_headings = _find_chapter_headings(lines, body_start, body_end)
	body_headings = _filter_body_headings(all_headings)
	section_starts = _find_first_section_lines(lines, body_start, body_end)

	# for each chapter, find the best start line and title
	chapter_info = {}
	for ch_num in range(1, 42):
		# prefer body (isolated) headings; they mark actual chapter starts
		ch_body = [(idx, num) for idx, num in body_headings if num == ch_num]
		# get the first section marker (N.1 line) for this chapter
		sec_start = section_starts.get(ch_num)

		best_heading = None
		title = ""

		if ch_body:
			# use the body heading closest to (but before) the section start
			if sec_start is not None:
				candidates = [(idx, num) for idx, num in ch_body if idx < sec_start]
				if candidates:
					best_heading = max(candidates, key=lambda x: x[0])[0]
				else:
					best_heading = min(ch_body, key=lambda x: abs(x[0] - sec_start))[0]
			else:
				best_heading = ch_body[-1][0]

		if best_heading is not None:
			title = _extract_title_after_heading(lines, best_heading)
			start_line = best_heading
		elif sec_start is not None:
			# no body heading found; use the N.1 section line as start
			# search backwards briefly for a chapter heading or title
			start_line = sec_start
			heading_pattern = _build_chapter_heading_pattern()
			for k in range(sec_start - 1, max(sec_start - 30, body_start), -1):
				stripped = lines[k].strip()
				if heading_pattern.match(stripped):
					start_line = k
					title = _extract_title_after_heading(lines, k)
					break
			if not title:
				title = _extract_title_from_toc(lines, ch_num)
		else:
			# last resort: use any heading (including section intro ones)
			ch_all = [(idx, num) for idx, num in all_headings if num == ch_num]
			if ch_all:
				best_heading = ch_all[-1][0]
				title = _extract_title_after_heading(lines, best_heading)
				start_line = best_heading
			else:
				continue

		# if title is still empty, try extracting from the TOC
		if not title:
			title = _extract_title_from_toc(lines, ch_num)

		chapter_info[ch_num] = (start_line, title)

	# enforce monotonic ordering: chapter N must start before chapter N+1
	sorted_chs = sorted(chapter_info.keys())
	for i in range(1, len(sorted_chs)):
		prev_ch = sorted_chs[i - 1]
		curr_ch = sorted_chs[i]
		prev_start = chapter_info[prev_ch][0]
		curr_start = chapter_info[curr_ch][0]
		if curr_start <= prev_start:
			# override: use the N.1 section line if it gives a better position
			sec = section_starts.get(curr_ch)
			if sec is not None and sec > prev_start:
				chapter_info[curr_ch] = (sec, chapter_info[curr_ch][1])
			else:
				# push to just after the previous chapter start
				chapter_info[curr_ch] = (prev_start + 1, chapter_info[curr_ch][1])

	# build boundary tuples with end lines
	sorted_chapters = sorted(chapter_info.keys())
	boundaries = []
	for idx, ch_num in enumerate(sorted_chapters):
		start_line = chapter_info[ch_num][0]
		title = chapter_info[ch_num][1]
		if idx + 1 < len(sorted_chapters):
			next_ch = sorted_chapters[idx + 1]
			end_line = chapter_info[next_ch][0] - 1
		else:
			end_line = body_end - 1
		boundaries.append((start_line, end_line, ch_num, title))

	return boundaries

#============================================
def extract_sections(chapter_lines: list) -> list:
	"""Extract numbered sections from a chapter's lines.

	Looks for section headings in the format 'N.M  Section Title'
	(e.g. '1.1  Living Systems Require a Limited Variety of Atoms').

	Args:
		chapter_lines: list of text lines from a single chapter.

	Returns:
		List of dicts with keys 'section_num' (str like '1.1') and
		'title' (str).
	"""
	# detect the chapter number from section patterns in the lines
	ch_num_pattern = re.compile(r'^(\d+)\.\d+\s+[A-Z]')
	detected_ch = None
	for line in chapter_lines:
		m = ch_num_pattern.match(line.strip())
		if m:
			detected_ch = int(m.group(1))
			break

	# pattern: digits.digits followed by whitespace and title text starting uppercase
	section_pattern = re.compile(r'^(\d+)\.(\d+)\s+([A-Z].+)')
	sections = []
	seen = set()
	for i, line in enumerate(chapter_lines):
		stripped = line.strip()
		m = section_pattern.match(stripped)
		if m:
			major = int(m.group(1))
			# skip sections that do not belong to this chapter
			if detected_ch is not None and major != detected_ch:
				continue
			sec_num = f"{m.group(1)}.{m.group(2)}"
			# skip if already seen (avoids duplicates from summary, etc.)
			if sec_num in seen:
				continue
			seen.add(sec_num)
			# extract the full title, which may span multiple lines
			# (blank lines may separate continuation text in raw textbook)
			title_text = m.group(3).strip()
			blank_count = 0
			for j in range(i + 1, min(i + 8, len(chapter_lines))):
				next_stripped = chapter_lines[j].strip()
				if not next_stripped:
					blank_count += 1
					# allow up to 2 consecutive blank lines
					if blank_count > 2:
						break
					continue
				blank_count = 0
				# stop if next line is another section or heading
				if re.match(r'^\d+\.\d+\s', next_stripped):
					break
				if re.match(r'^[Cc]\s*[Hh]\s*[Aa]\s*[Pp]', next_stripped):
					break
				# stop if line looks like body text (long sentence, not title-like)
				if len(next_stripped) > 60:
					break
				# title continuation: accept alphabetic starts (incl. lowercase articles)
				if next_stripped[0].isalpha():
					title_text += " " + next_stripped
				else:
					break
			# clean up whitespace and tab characters
			title_text = re.sub(r'\s+', ' ', title_text).strip()
			# remove trailing page numbers
			title_text = re.sub(r'\s+\d+\s*$', '', title_text)
			sections.append({
				"section_num": sec_num,
				"title": title_text,
			})
	return sections

#============================================
def extract_key_terms(chapter_lines: list) -> list:
	"""Extract key terms with page references from a chapter.

	Looks for a 'Key Terms' or 'KEY TERMS' heading in the chapter
	end material, then parses 'term (p. NN)' entries.

	Args:
		chapter_lines: list of text lines from a single chapter.

	Returns:
		List of dicts with keys 'term' (str) and 'page' (int or None).
	"""
	# find the key terms heading (case-insensitive, varied capitalization)
	key_terms_pattern = re.compile(r'^key\s+terms?\s*$', re.IGNORECASE)
	start_idx = None
	for i, line in enumerate(chapter_lines):
		stripped = line.strip()
		if key_terms_pattern.match(stripped):
			start_idx = i + 1
			break

	if start_idx is None:
		return []

	# parse term entries until we hit a different section
	# stop patterns: PROBLEMS, Answers to, Summary, Chapter heading
	stop_pattern = re.compile(
		r'^(problems|answers\s+to|summary|selected\s+readings)',
		re.IGNORECASE,
	)
	# pattern for term with page reference: "term (p. NN)"
	term_page_pattern = re.compile(r'^(.+?)\s*\(p\.\s*(\d+)\)')
	# pattern for term without page reference
	term_only_pattern = re.compile(r'^([A-Za-z].+)')

	terms = []
	for i in range(start_idx, len(chapter_lines)):
		stripped = chapter_lines[i].strip()
		if not stripped:
			continue
		# check if we hit a stop section
		if stop_pattern.match(stripped):
			break
		# check for bare page numbers (page artifacts)
		if re.match(r'^\d{1,4}$', stripped):
			continue
		# try to match term with page reference
		m = term_page_pattern.match(stripped)
		if m:
			term_name = m.group(1).strip()
			page_num = int(m.group(2))
			terms.append({
				"term": term_name,
				"page": page_num,
			})
			continue
		# check for continuation of previous page pattern on same line
		# e.g. "bonds) (p. 20)" - partial entry from line break
		if stripped.startswith("(p.") or stripped.startswith("bonds)"):
			continue
		# try to match a term without page reference (rare)
		m2 = term_only_pattern.match(stripped)
		if m2:
			term_name = m2.group(1).strip()
			# skip if it looks like a heading or non-term text
			if len(term_name) > 3 and not term_name[0].isdigit():
				terms.append({
					"term": term_name,
					"page": None,
				})

	return terms

#============================================
def run_tests() -> None:
	"""Run basic assertion tests for the module functions."""
	# test extract_sections with sample input
	sample_lines = [
		"C h a p t e r  1",
		"Biochemistry and the Unity of Life",
		"1.1  Living Systems Require a Limited Variety of Atoms",
		"1.2  There Are Four Major Classes of Biomolecules",
		"Body text here about biochemistry...",
		"1.3  The Central Dogma Describes the Basic Principles",
		"0.5  some non-section text should be ignored",
	]
	sections = extract_sections(sample_lines)
	assert len(sections) == 3, f"Expected 3 sections, got {len(sections)}"
	assert sections[0]["section_num"] == "1.1"
	assert "Living Systems" in sections[0]["title"]
	assert sections[1]["section_num"] == "1.2"
	assert sections[2]["section_num"] == "1.3"

	# test extract_key_terms with sample input
	term_lines = [
		"kEy TERMS",
		"unity of biochemistry (p. 3)",
		"proteins (p. 5)",
		"nucleic acids (p. 6)",
		"PROBLEMS",
		"1.  E. coli and elephants.",
	]
	terms = extract_key_terms(term_lines)
	assert len(terms) == 3, f"Expected 3 terms, got {len(terms)}"
	assert terms[0]["term"] == "unity of biochemistry"
	assert terms[0]["page"] == 3
	assert terms[1]["term"] == "proteins"
	assert terms[1]["page"] == 5

	# test detect_chapter_boundaries with minimal input
	# (full test requires actual textbook file)
	empty_result = detect_chapter_boundaries([])
	assert empty_result == []

	print("All textbook_chapters tests passed.")

#============================================
def main() -> None:
	"""Main entry point: run tests and show chapter info from textbook."""
	run_tests()

	# try to load and analyze the actual textbook file
	textbook_path = "artifacts/Tymoczko_3rd_edition.txt"
	import os
	if not os.path.exists(textbook_path):
		print(f"Textbook file not found at {textbook_path}, skipping analysis.")
		return

	# read and clean the textbook
	with open(textbook_path, "r", encoding="utf-8", errors="replace") as f:
		raw_text = f.read()
	# normalize whitespace using the cleaning module
	raw_text = textbook_clean.normalize_whitespace(raw_text)
	lines = raw_text.split("\n")
	print(f"Loaded {len(lines)} lines from textbook.")

	# detect chapter boundaries
	boundaries = detect_chapter_boundaries(lines)
	print(f"\nFound {len(boundaries)} chapters:")
	for start, end, ch_num, title in boundaries:
		line_count = end - start + 1
		print(f"  Chapter {ch_num:2d}: lines {start:6d}-{end:6d} ({line_count:5d} lines) - {title}")

	# show sections for the first chapter as a sample
	if boundaries:
		first = boundaries[0]
		ch_lines = lines[first[0]:first[1] + 1]
		sections = extract_sections(ch_lines)
		print(f"\nSections in Chapter {first[2]}:")
		for sec in sections:
			print(f"  {sec['section_num']}  {sec['title']}")

		# show key terms for the first chapter
		terms = extract_key_terms(ch_lines)
		print(f"\nKey terms in Chapter {first[2]} ({len(terms)} terms):")
		for term_info in terms[:5]:
			page_str = f"p. {term_info['page']}" if term_info['page'] else "no page"
			print(f"  {term_info['term']} ({page_str})")
		if len(terms) > 5:
			print(f"  ... and {len(terms) - 5} more terms")

#============================================
if __name__ == "__main__":
	main()
