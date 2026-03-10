#!/usr/bin/env python3

"""Parse the Biology 2e (OpenStax) textbook into structured JSON files.

Reads the raw textbook text, splits it into chapters, and extracts
questions (visual connection, review, critical thinking) for each chapter.
Writes one JSON file per chapter to structured/chapters/.
"""

# Standard Library
import os
import re
import json
import argparse

# local repo modules
import textbook_clean

#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Parse Biology 2e textbook into structured chapter JSON files.",
	)
	parser.add_argument(
		'-i', '--input', dest='input_file',
		default='artifacts/Biology2e.txt',
		help="Path to the raw textbook text file",
	)
	parser.add_argument(
		'-o', '--output-dir', dest='output_dir',
		default='structured/chapters',
		help="Output directory for chapter JSON files",
	)
	args = parser.parse_args()
	return args

#============================================
def make_slug(title: str) -> str:
	"""Convert a chapter title into a filename-safe slug.

	Args:
		title: chapter title string.

	Returns:
		Lowercase slug with underscores, ASCII-safe.
	"""
	# lowercase and replace non-alphanumeric with underscores
	slug = re.sub(r'[^a-z0-9]+', '_', title.lower())
	# strip leading/trailing underscores and collapse multiples
	slug = re.sub(r'_+', '_', slug).strip('_')
	# truncate to a reasonable length for filenames
	if len(slug) > 50:
		slug = slug[:50].rstrip('_')
	return slug

#============================================
def detect_chapter_boundaries(lines: list) -> list:
	"""Detect chapter boundaries using CHAPTER N pattern.

	Looks for lines matching "CHAPTER N" followed by a title line,
	then "CHAPTER OUTLINE". Skips table-of-contents entries by
	requiring CHAPTER OUTLINE to appear nearby.

	Args:
		lines: list of all text lines.

	Returns:
		List of tuples (start_line, end_line, chapter_num, title).
		end_line is set to the line before the next chapter starts.
	"""
	# pattern for "CHAPTER N" lines
	chapter_pattern = re.compile(r'^CHAPTER\s+(\d+)$')
	boundaries = []
	for i, line in enumerate(lines):
		match = chapter_pattern.match(line.strip())
		if not match:
			continue
		ch_num = int(match.group(1))
		# find the title: skip blank lines after CHAPTER N
		title = None
		for j in range(i + 1, min(i + 5, len(lines))):
			if lines[j].strip():
				title = lines[j].strip()
				break
		if title is None:
			continue
		# verify CHAPTER OUTLINE appears within 15 lines
		has_outline = False
		for j in range(i + 1, min(i + 15, len(lines))):
			if lines[j].strip() == 'CHAPTER OUTLINE':
				has_outline = True
				break
		if not has_outline:
			continue
		boundaries.append((i, ch_num, title))
	# set end lines: each chapter ends where the next one begins
	result = []
	for idx in range(len(boundaries)):
		start, ch_num, title = boundaries[idx]
		if idx + 1 < len(boundaries):
			end = boundaries[idx + 1][0] - 1
		else:
			end = len(lines) - 1
		result.append((start, end, ch_num, title))
	return result

#============================================
def is_page_artifact(line: str) -> bool:
	"""Check if a line is a page artifact to filter out.

	Detects bare page numbers, "Access for free" footers,
	and page headers like "N * Section Name".

	Args:
		line: text line to check.

	Returns:
		True if the line should be filtered out.
	"""
	stripped = line.strip()
	# bare page numbers (1-4 digits)
	if re.match(r'^\d{1,4}$', stripped):
		return True
	# "Access for free at openstax.org"
	if 'Access for free at openstax.org' in stripped:
		return True
	# page headers like "1 * Review Questions" or "2 * The Chemical Foundation"
	# the bullet is various chars: literal dot, bullet char, etc.
	if re.match(r'^\d+\s+[\u2022\u00b7\u2023•·]\s+', stripped):
		return True
	return False

#============================================
def extract_questions_from_section(
	section_lines: list,
	question_type: str,
) -> list:
	"""Extract numbered questions from a question section.

	Parses lines for questions starting with "N. " and for MC
	options starting with "a. ", "b. ", etc.

	Args:
		section_lines: lines belonging to one question section.
		question_type: one of "visual_connection", "review", "critical_thinking".

	Returns:
		List of problem dicts with number, text, type, and optional choices.
	"""
	# filter out page artifacts
	cleaned = []
	for line in section_lines:
		if not is_page_artifact(line):
			cleaned.append(line)
	# pattern for question start: "N. " at beginning of line
	question_pattern = re.compile(r'^(\d+)\.\s+(.*)')
	# pattern for MC choice: "a. ", "b. ", etc.
	choice_pattern = re.compile(r'^([a-d])\.\s+(.*)')
	problems = []
	current_question = None
	current_text_parts = []
	current_choices = {}
	current_choice_key = None
	current_choice_parts = []

	def finalize_choice():
		"""Save the current choice if one is being built."""
		if current_choice_key and current_choice_parts:
			choice_text = ' '.join(current_choice_parts).strip()
			current_choices[current_choice_key] = choice_text

	def finalize_question():
		"""Save the current question to problems list."""
		if current_question is not None:
			finalize_choice()
			text = ' '.join(current_text_parts).strip()
			problem = {
				"number": current_question,
				"text": text,
				"type": question_type,
			}
			if current_choices:
				problem["choices"] = dict(current_choices)
			problems.append(problem)

	for line in cleaned:
		stripped = line.strip()
		if not stripped:
			continue
		# check for new question
		q_match = question_pattern.match(stripped)
		if q_match:
			# save previous question
			finalize_question()
			# start new question
			current_question = int(q_match.group(1))
			current_text_parts = [q_match.group(2)]
			current_choices = {}
			current_choice_key = None
			current_choice_parts = []
			continue
		# check for MC choice
		c_match = choice_pattern.match(stripped)
		if c_match and current_question is not None:
			# save previous choice
			finalize_choice()
			current_choice_key = c_match.group(1)
			current_choice_parts = [c_match.group(2)]
			continue
		# continuation line
		if current_question is not None:
			if current_choice_key:
				# continuation of a choice
				current_choice_parts.append(stripped)
			else:
				# continuation of question text
				current_text_parts.append(stripped)
	# save the last question
	finalize_question()
	return problems

#============================================
def extract_chapter_questions(lines: list, start: int, end: int) -> list:
	"""Extract all questions from a chapter's end-of-chapter section.

	Finds the Visual Connection Questions, Review Questions, and
	Critical Thinking Questions sections within the chapter lines.

	Args:
		lines: full textbook lines.
		start: chapter start line index.
		end: chapter end line index.

	Returns:
		List of problem dicts.
	"""
	chapter_lines = lines[start:end + 1]
	# find section boundaries within chapter
	section_headers = {
		'Visual Connection Questions': 'visual_connection',
		'Review Questions': 'review',
		'Critical Thinking Questions': 'critical_thinking',
	}
	# find positions of each section header
	section_positions = []
	for i, line in enumerate(chapter_lines):
		stripped = line.strip()
		if stripped in section_headers:
			section_positions.append((i, section_headers[stripped]))
	# extract questions from each section
	all_problems = []
	for idx, (pos, qtype) in enumerate(section_positions):
		# section runs from header to next header or end of chapter
		sec_start = pos + 1
		if idx + 1 < len(section_positions):
			sec_end = section_positions[idx + 1][0]
		else:
			sec_end = len(chapter_lines)
		section_lines = chapter_lines[sec_start:sec_end]
		problems = extract_questions_from_section(section_lines, qtype)
		all_problems.extend(problems)
	return all_problems

#============================================
def main() -> None:
	"""Main entry point: parse Biology 2e and write chapter JSON files."""
	args = parse_args()
	# validate input file
	if not os.path.exists(args.input_file):
		raise FileNotFoundError(f"Textbook file not found: {args.input_file}")
	# read the textbook
	with open(args.input_file, "r", encoding="utf-8", errors="replace") as f:
		raw_text = f.read()
	# normalize whitespace
	raw_text = textbook_clean.normalize_whitespace(raw_text)
	lines = raw_text.split("\n")
	print(f"Loaded {len(lines)} lines from {args.input_file}")
	# detect chapter boundaries
	boundaries = detect_chapter_boundaries(lines)
	print(f"Found {len(boundaries)} chapters")
	# create output directory
	os.makedirs(args.output_dir, exist_ok=True)
	# process each chapter
	total_problems = 0
	for boundary in boundaries:
		start, end, ch_num, title = boundary
		slug = make_slug(title)
		filename = f"bio2e_ch{ch_num:02d}_{slug}.json"
		filepath = os.path.join(args.output_dir, filename)
		# extract questions
		problems = extract_chapter_questions(lines, start, end)
		total_problems += len(problems)
		# build chapter data
		chapter_data = {
			"chapter_num": ch_num,
			"title": title,
			"slug": slug,
			"problems": problems,
			"answers": {},
		}
		# write JSON file
		with open(filepath, "w", encoding="utf-8") as f:
			json.dump(chapter_data, f, indent=2, ensure_ascii=True)
		# report progress
		n_vc = sum(1 for p in problems if p["type"] == "visual_connection")
		n_rv = sum(1 for p in problems if p["type"] == "review")
		n_ct = sum(1 for p in problems if p["type"] == "critical_thinking")
		print(
			f"  Ch {ch_num:2d}: {n_vc:2d} visual, {n_rv:2d} review, "
			f"{n_ct:2d} critical -> {filename}"
		)
	print(f"\nTotal: {total_problems} problems across {len(boundaries)} chapters")
	print(f"Output written to {args.output_dir}/")

#============================================
if __name__ == "__main__":
	main()
