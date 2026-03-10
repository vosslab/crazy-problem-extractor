#!/usr/bin/env python3

"""Tests for parse_biology2e.py output."""

# Standard Library
import os
import re
import json
import glob

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
CHAPTERS_DIR = os.path.join(REPO_ROOT, "structured", "chapters")
EXPECTED_CHAPTERS = 47
QUESTION_TYPES = {"visual_connection", "review", "critical_thinking"}

#============================================
def get_bio2e_files() -> list:
	"""Return sorted list of bio2e chapter JSON file paths."""
	pattern = os.path.join(CHAPTERS_DIR, "bio2e_ch*.json")
	files = sorted(glob.glob(pattern))
	return files

#============================================
def load_chapter(filepath: str) -> dict:
	"""Load and return a chapter JSON file."""
	with open(filepath, "r", encoding="utf-8") as f:
		data = json.load(f)
	return data

#============================================
# collect all chapter files for parametrized tests
BIO2E_FILES = get_bio2e_files()

#============================================
def test_expected_chapter_count():
	"""Verify that all 47 chapter JSON files exist."""
	assert len(BIO2E_FILES) == EXPECTED_CHAPTERS, (
		f"Expected {EXPECTED_CHAPTERS} chapter files, found {len(BIO2E_FILES)}"
	)

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_chapter_has_required_keys(filepath: str):
	"""Each chapter JSON must have chapter_num, title, slug, problems, answers."""
	data = load_chapter(filepath)
	for key in ("chapter_num", "title", "slug", "problems", "answers"):
		assert key in data, f"Missing key '{key}' in {os.path.basename(filepath)}"

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_chapter_not_empty(filepath: str):
	"""Each chapter must have at least one problem."""
	data = load_chapter(filepath)
	assert len(data["problems"]) > 0, (
		f"No problems in {os.path.basename(filepath)}"
	)

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_problems_have_required_fields(filepath: str):
	"""Each problem must have number, text, and type fields."""
	data = load_chapter(filepath)
	for prob in data["problems"]:
		assert "number" in prob, f"Problem missing 'number' in {os.path.basename(filepath)}"
		assert "text" in prob, f"Problem missing 'text' in {os.path.basename(filepath)}"
		assert "type" in prob, f"Problem missing 'type' in {os.path.basename(filepath)}"

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_problem_types_valid(filepath: str):
	"""Each problem type must be one of the three recognized types."""
	data = load_chapter(filepath)
	for prob in data["problems"]:
		assert prob["type"] in QUESTION_TYPES, (
			f"Unknown type '{prob['type']}' in {os.path.basename(filepath)}"
		)

#============================================
def test_all_three_types_present():
	"""Across all chapters, all three question types must appear."""
	found_types = set()
	for filepath in BIO2E_FILES:
		data = load_chapter(filepath)
		for prob in data["problems"]:
			found_types.add(prob["type"])
	assert found_types == QUESTION_TYPES, (
		f"Missing question types: {QUESTION_TYPES - found_types}"
	)

#============================================
def test_review_questions_mostly_have_choices():
	"""At least 95% of review questions must have a choices dict with a-d keys.

	Some questions lose choices due to page-break artifacts in the
	source text, so we check the overall rate rather than every question.
	"""
	total_review = 0
	complete = 0
	for filepath in BIO2E_FILES:
		data = load_chapter(filepath)
		review_problems = [p for p in data["problems"] if p["type"] == "review"]
		for prob in review_problems:
			total_review += 1
			choices = prob.get("choices", {})
			if all(letter in choices for letter in ("a", "b", "c", "d")):
				complete += 1
	# at least 95% should have full a-d choices
	ratio = complete / total_review if total_review else 0
	assert ratio >= 0.95, (
		f"Only {complete}/{total_review} ({ratio:.1%}) review questions "
		f"have complete a-d choices (expected >= 95%)"
	)

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_slug_format(filepath: str):
	"""Slug must be lowercase with underscores, no special chars."""
	data = load_chapter(filepath)
	slug = data["slug"]
	assert re.match(r'^[a-z0-9_]+$', slug), (
		f"Invalid slug '{slug}' in {os.path.basename(filepath)}"
	)

#============================================
@pytest.mark.parametrize("filepath", BIO2E_FILES, ids=[
	os.path.basename(f) for f in BIO2E_FILES
])
def test_chapter_num_matches_filename(filepath: str):
	"""Chapter number in JSON must match the NN in the filename."""
	data = load_chapter(filepath)
	basename = os.path.basename(filepath)
	# extract number from filename like bio2e_ch01_...
	match = re.search(r'bio2e_ch(\d+)_', basename)
	assert match, f"Cannot parse chapter number from {basename}"
	file_num = int(match.group(1))
	assert data["chapter_num"] == file_num, (
		f"Chapter num {data['chapter_num']} != filename num {file_num}"
	)
