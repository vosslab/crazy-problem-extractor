#!/usr/bin/env python3

"""Parse the Tymoczko biochemistry textbook into structured JSON files.

Reads the raw textbook text, splits it into chapters, and extracts
sections, key terms, problems, and answers for each chapter. Writes
one JSON file per chapter to structured/chapters/.
"""

# Standard Library
import os
import re
import json
import argparse

# local repo modules
import textbook_clean
import textbook_chapters
import textbook_problems
import textbook_answers

#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Parse textbook into structured chapter JSON files.",
	)
	parser.add_argument(
		'-i', '--input', dest='input_file',
		default='artifacts/Tymoczko_3rd_edition.txt',
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
def build_chapter_data(
	lines: list,
	chapter_boundary: tuple,
	answer_boundaries: list,
) -> dict:
	"""Build structured data for a single chapter.

	Extracts sections, key terms, problems (standard, challenge, data
	interpretation), and answers.

	Args:
		lines: full textbook lines list.
		chapter_boundary: tuple (start_line, end_line, chapter_num, title).
		answer_boundaries: list of (start, end, ch_num) from answer key.

	Returns:
		Dict with chapter_num, title, sections, key_terms, problems,
		challenge_problems, data_interpretation_problems, and answers.
	"""
	start, end, ch_num, title = chapter_boundary
	# slice the chapter lines
	chapter_lines = lines[start:end + 1]

	# extract sections
	sections = textbook_chapters.extract_sections(chapter_lines)

	# extract key terms
	key_terms = textbook_chapters.extract_key_terms(chapter_lines)

	# extract problems
	problems = textbook_problems.extract_problems(chapter_lines)
	challenge = textbook_problems.extract_challenge_problems(chapter_lines)
	data_interp = textbook_problems.extract_data_interpretation_problems(chapter_lines)

	# extract answers from the answer key
	answers = {}
	for a_start, a_end, a_ch in answer_boundaries:
		if a_ch == ch_num:
			answer_lines = lines[a_start:a_end + 1]
			answers = textbook_answers.extract_answer_key(answer_lines, ch_num)
			break

	# build the structured data dict
	chapter_data = {
		"chapter_num": ch_num,
		"title": title,
		"sections": sections,
		"key_terms": key_terms,
		"problems": problems,
		"challenge_problems": challenge,
		"data_interpretation_problems": data_interp,
		"answers": answers,
	}
	return chapter_data

#============================================
def main() -> None:
	"""Main entry point: parse textbook and write chapter JSON files."""
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

	# detect chapter boundaries in the body text
	boundaries = textbook_chapters.detect_chapter_boundaries(lines)
	print(f"Found {len(boundaries)} chapters")

	# detect answer key boundaries
	answer_boundaries = textbook_answers.detect_answer_section_boundaries(lines)
	print(f"Found {len(answer_boundaries)} answer sections")

	# create output directory
	os.makedirs(args.output_dir, exist_ok=True)

	# process each chapter
	total_problems = 0
	total_terms = 0
	for boundary in boundaries:
		ch_num = boundary[2]
		title = boundary[3]
		slug = make_slug(title)
		filename = f"ch{ch_num:02d}_{slug}.json"
		filepath = os.path.join(args.output_dir, filename)

		# build chapter data
		chapter_data = build_chapter_data(lines, boundary, answer_boundaries)

		# convert answer keys from int keys to string keys for JSON
		if chapter_data["answers"]:
			chapter_data["answers"] = {
				str(k): v for k, v in chapter_data["answers"].items()
			}

		# write JSON file
		with open(filepath, "w", encoding="utf-8") as f:
			json.dump(chapter_data, f, indent=2, ensure_ascii=True)

		# report progress
		n_prob = len(chapter_data["problems"])
		n_chal = len(chapter_data["challenge_problems"])
		n_data = len(chapter_data["data_interpretation_problems"])
		n_terms = len(chapter_data["key_terms"])
		n_answers = len(chapter_data["answers"])
		total_problems += n_prob + n_chal + n_data
		total_terms += n_terms
		print(
			f"  Ch {ch_num:2d}: {n_prob:2d} problems, {n_chal:2d} challenge, "
			f"{n_data:2d} data-interp, {n_terms:2d} terms, "
			f"{n_answers:2d} answers -> {filename}"
		)

	print(f"\nTotal: {total_problems} problems, {total_terms} key terms")
	print(f"Output written to {args.output_dir}/")

#============================================
if __name__ == "__main__":
	main()
