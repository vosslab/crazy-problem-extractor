"""Tests for _chaotic_dispatch module."""

# Standard Library
import os
import sys

import pytest
import yaml

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import _chaotic_dispatch


#============================================
def test_extract_slug_simple():
	"""Test basic slug extraction from a short chapter filename."""
	result = _chaotic_dispatch.extract_slug("ch03_amino_acids.json")
	assert result == "amino_acids"


#============================================
def test_extract_slug_long_name():
	"""Test slug extraction from a long chapter filename."""
	filename = "ch33_the_structure_of_informational_macromolecules_dna.json"
	result = _chaotic_dispatch.extract_slug(filename)
	assert result == "the_structure_of_informational_macromolecules_dna"


#============================================
def test_build_manifest_filters_by_answers():
	"""Test that build_manifest only includes problems with answers."""
	chapter_data = {
		"chapter_num": 3,
		"title": "Amino Acids",
		"problems": [
			{"number": 1, "text": "Problem one"},
			{"number": 2, "text": "Problem two"},
			{"number": 3, "text": "Problem three"},
		],
		"answers": {
			"1": "Answer one",
			"3": "Answer three",
		},
	}
	manifest = _chaotic_dispatch.build_manifest(chapter_data, "amino_acids")
	# only problems 1 and 3 have answers, so manifest should have 2
	assert len(manifest["problems"]) == 2
	included_numbers = [p["number"] for p in manifest["problems"]]
	assert 1 in included_numbers
	assert 3 in included_numbers
	assert 2 not in included_numbers


#============================================
def test_build_manifest_includes_challenge():
	"""Test that challenge problems with answers are included."""
	chapter_data = {
		"chapter_num": 5,
		"title": "Enzymes",
		"problems": [
			{"number": 1, "text": "Standard problem"},
		],
		"challenge_problems": [
			{"number": 10, "text": "Challenge problem"},
		],
		"answers": {
			"1": "Standard answer",
			"10": "Challenge answer",
		},
	}
	manifest = _chaotic_dispatch.build_manifest(chapter_data, "enzymes")
	assert len(manifest["problems"]) == 2
	# verify the challenge problem is present with correct type
	challenge_entries = [
		p for p in manifest["problems"] if p["type"] == "challenge"
	]
	assert len(challenge_entries) == 1
	assert challenge_entries[0]["number"] == 10


#============================================
def test_build_manifest_sorts_by_number():
	"""Test that manifest problems are sorted by problem number."""
	chapter_data = {
		"chapter_num": 7,
		"title": "Lipids",
		"problems": [
			{"number": 5, "text": "Fifth"},
			{"number": 2, "text": "Second"},
			{"number": 9, "text": "Ninth"},
		],
		"challenge_problems": [
			{"number": 1, "text": "First challenge"},
		],
		"answers": {
			"5": "a5",
			"2": "a2",
			"9": "a9",
			"1": "a1",
		},
	}
	manifest = _chaotic_dispatch.build_manifest(chapter_data, "lipids")
	numbers = [p["number"] for p in manifest["problems"]]
	assert numbers == sorted(numbers)
	assert numbers == [1, 2, 5, 9]


#============================================
def test_create_staging_dirs(tmp_path):
	"""Test that staging directories are created with correct names."""
	dirs = _chaotic_dispatch.create_staging_dirs(
		str(tmp_path), 3, "amino_acids", 2,
	)
	# expect 2 coder dirs plus 1 merged dir
	assert len(dirs) == 3
	for d in dirs:
		assert os.path.isdir(d)
	# verify coder directory names
	assert dirs[0].endswith(os.path.join("coder_1", "ch03_amino_acids"))
	assert dirs[1].endswith(os.path.join("coder_2", "ch03_amino_acids"))
	# verify merged directory name
	assert dirs[2].endswith(os.path.join("merged", "ch03_amino_acids"))


#============================================
def test_write_manifest(tmp_path):
	"""Test that write_manifest writes valid YAML content."""
	manifest = {
		"chapter_num": 3,
		"title": "Amino Acids",
		"slug": "amino_acids",
		"problems": [
			{"number": 1, "text": "Q1", "answer": "A1", "type": "standard"},
		],
	}
	yaml_path = _chaotic_dispatch.write_manifest(str(tmp_path), 3, manifest)
	# verify the file exists
	assert os.path.isfile(yaml_path)
	assert yaml_path.endswith("ch03_manifest.yaml")
	# read back and verify content
	with open(yaml_path, "r") as f:
		loaded = yaml.safe_load(f)
	assert loaded["chapter_num"] == 3
	assert loaded["title"] == "Amino Acids"
	assert loaded["slug"] == "amino_acids"
	assert len(loaded["problems"]) == 1
	assert loaded["problems"][0]["number"] == 1


#============================================
def test_find_chapter_json(tmp_path):
	"""Test that find_chapter_json locates an existing chapter JSON file."""
	# create the expected directory structure
	chapters_dir = tmp_path / "structured" / "chapters"
	chapters_dir.mkdir(parents=True)
	fake_json = chapters_dir / "ch03_amino_acids.json"
	fake_json.write_text("{}")
	result = _chaotic_dispatch.find_chapter_json(str(tmp_path), 3)
	assert result == str(fake_json)


#============================================
def test_find_chapter_json_missing(tmp_path):
	"""Test that find_chapter_json raises FileNotFoundError for missing chapter."""
	# create empty chapters directory with no matching files
	chapters_dir = tmp_path / "structured" / "chapters"
	chapters_dir.mkdir(parents=True)
	with pytest.raises(FileNotFoundError):
		_chaotic_dispatch.find_chapter_json(str(tmp_path), 99)


#============================================
def test_build_manifest_deduplicates():
	"""Test that build_manifest keeps only the first entry per problem number."""
	chapter_data = {
		"chapter_num": 3,
		"title": "Amino Acids",
		"problems": [
			{"number": 4, "text": "First problem 4"},
			{"number": 5, "text": "Problem five"},
			{"number": 4, "text": "Duplicate problem 4"},
		],
		"answers": {
			"4": "Answer four",
			"5": "Answer five",
		},
	}
	manifest = _chaotic_dispatch.build_manifest(chapter_data, "amino_acids")
	# should have 2 problems, not 3
	assert len(manifest["problems"]) == 2
	# only the first problem 4 text should be kept
	p4_entries = [p for p in manifest["problems"] if p["number"] == 4]
	assert len(p4_entries) == 1
	assert p4_entries[0]["text"] == "First problem 4"


#============================================
def test_assign_problems_modular_basic():
	"""Test modular assignment with 6 problems and 3 coders."""
	problem_numbers = [1, 2, 3, 4, 5, 6]
	assignments = _chaotic_dispatch.assign_problems_modular(
		problem_numbers, 3
	)
	# coder 1 gets index 0, 3 -> problems 1, 4
	assert assignments[1]["required"] == [1, 4]
	# coder 2 gets index 1, 4 -> problems 2, 5
	assert assignments[2]["required"] == [2, 5]
	# coder 3 gets index 2, 5 -> problems 3, 6
	assert assignments[3]["required"] == [3, 6]


#============================================
def test_assign_problems_modular_optional():
	"""Test that optional lists contain all non-required problems."""
	problem_numbers = [1, 2, 3, 4, 5]
	assignments = _chaotic_dispatch.assign_problems_modular(
		problem_numbers, 3
	)
	# coder 1 required: [1, 4], optional: [2, 3, 5]
	assert assignments[1]["optional"] == [2, 3, 5]
	# coder 2 required: [2, 5], optional: [1, 3, 4]
	assert assignments[2]["optional"] == [1, 3, 4]
	# coder 3 required: [3], optional: [1, 2, 4, 5]
	assert assignments[3]["optional"] == [1, 2, 4, 5]


#============================================
def test_assign_problems_modular_uneven():
	"""Test that coders get uneven counts when problems not divisible."""
	# 18 problems, 8 coders: first 2 coders get 3, rest get 2
	problem_numbers = list(range(1, 19))
	assignments = _chaotic_dispatch.assign_problems_modular(
		problem_numbers, 8
	)
	# coders 1-2 should get 3 required problems
	assert len(assignments[1]["required"]) == 3
	assert len(assignments[2]["required"]) == 3
	# coders 3-8 should get 2 required problems
	for coder in range(3, 9):
		assert len(assignments[coder]["required"]) == 2
	# every problem should be assigned to exactly one coder
	all_required = []
	for coder in range(1, 9):
		all_required.extend(assignments[coder]["required"])
	assert sorted(all_required) == list(range(1, 19))


#============================================
def test_assign_problems_modular_ch03():
	"""Test modular assignment for ch03 (18 problems, 8 coders).

	Sorted problems: [1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19]
	Index-based assignment: coder = (index % 8) + 1
	"""
	# ch03 has problems 1-7, 9-19 (no problem 8)
	problem_numbers = list(range(1, 8)) + list(range(9, 20))
	assignments = _chaotic_dispatch.assign_problems_modular(
		problem_numbers, 8
	)
	# index 0->c1(p1), 8->c1(p10), 16->c1(p18)
	assert assignments[1]["required"] == [1, 10, 18]
	# index 1->c2(p2), 9->c2(p11), 17->c2(p19)
	assert assignments[2]["required"] == [2, 11, 19]
	# index 7->c8(p9), 15->c8(p17)
	assert assignments[8]["required"] == [9, 17]
	# coders 1-2 get 3 required, coders 3-8 get 2 required
	for coder in range(1, 3):
		assert len(assignments[coder]["required"]) == 3
	for coder in range(3, 9):
		assert len(assignments[coder]["required"]) == 2
	# every problem assigned exactly once
	all_required = []
	for coder in range(1, 9):
		all_required.extend(assignments[coder]["required"])
	assert sorted(all_required) == sorted(problem_numbers)


#============================================
def test_write_assignments(tmp_path):
	"""Test that write_assignments creates YAML files for each coder."""
	assignments = {
		1: {"required": [1, 9], "optional": [2, 3]},
		2: {"required": [2, 10], "optional": [1, 3]},
	}
	paths = _chaotic_dispatch.write_assignments(
		str(tmp_path), 3, "amino_acids", assignments
	)
	assert len(paths) == 2
	# verify files exist and contain correct data
	for path in paths:
		assert os.path.isfile(path)
		assert path.endswith("assignments.yaml")
	# read back coder 1 assignment
	with open(paths[0], "r") as f:
		loaded = yaml.safe_load(f)
	assert loaded["required"] == [1, 9]
	assert loaded["optional"] == [2, 3]


#============================================
def test_extract_slug_bio2e_prefix():
	"""Test slug extraction with bio2e_ch prefix."""
	result = _chaotic_dispatch.extract_slug(
		"bio2e_ch05_the_structure_of_cells.json", prefix="bio2e_ch"
	)
	assert result == "the_structure_of_cells"


#============================================
def test_find_chapter_json_bio2e_prefix(tmp_path):
	"""Test that find_chapter_json locates a bio2e-prefixed JSON file."""
	chapters_dir = tmp_path / "structured" / "chapters"
	chapters_dir.mkdir(parents=True)
	fake_json = chapters_dir / "bio2e_ch05_the_structure_of_cells.json"
	fake_json.write_text("{}")
	result = _chaotic_dispatch.find_chapter_json(
		str(tmp_path), 5, prefix="bio2e_ch"
	)
	assert result == str(fake_json)


#============================================
def test_create_staging_dirs_bio2e_prefix(tmp_path):
	"""Test staging dirs use bio2e_ch prefix in directory names."""
	dirs = _chaotic_dispatch.create_staging_dirs(
		str(tmp_path), 5, "the_structure_of_cells", 2,
		prefix="bio2e_ch",
	)
	assert len(dirs) == 3
	for d in dirs:
		assert os.path.isdir(d)
	# verify prefix in directory names
	assert dirs[0].endswith(
		os.path.join("coder_1", "bio2e_ch05_the_structure_of_cells")
	)
	assert dirs[2].endswith(
		os.path.join("merged", "bio2e_ch05_the_structure_of_cells")
	)


#============================================
def test_write_manifest_bio2e_prefix(tmp_path):
	"""Test that write_manifest uses bio2e_ch prefix in YAML filename."""
	manifest = {
		"chapter_num": 5,
		"title": "The Structure of Cells",
		"slug": "the_structure_of_cells",
		"problems": [],
	}
	yaml_path = _chaotic_dispatch.write_manifest(
		str(tmp_path), 5, manifest, prefix="bio2e_ch"
	)
	assert os.path.isfile(yaml_path)
	assert yaml_path.endswith("bio2e_ch05_manifest.yaml")


#============================================
def test_write_assignments_bio2e_prefix(tmp_path):
	"""Test that write_assignments uses bio2e_ch prefix in directory names."""
	assignments = {
		1: {"required": [1], "optional": [2]},
	}
	paths = _chaotic_dispatch.write_assignments(
		str(tmp_path), 5, "the_structure_of_cells",
		assignments, prefix="bio2e_ch",
	)
	assert len(paths) == 1
	assert "bio2e_ch05_the_structure_of_cells" in paths[0]


#============================================
def test_default_prefix_unchanged():
	"""Test that default prefix='ch' preserves original behavior."""
	# extract_slug default should match original behavior
	result = _chaotic_dispatch.extract_slug("ch03_amino_acids.json")
	assert result == "amino_acids"
	# explicit default should give same result
	result_explicit = _chaotic_dispatch.extract_slug(
		"ch03_amino_acids.json", prefix="ch"
	)
	assert result_explicit == result
