"""Tests for _promote_winners module."""

# Standard Library
import os
import sys

import pytest
import yaml

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import _promote_winners


#============================================
def test_find_merged_file():
	"""Test that find_merged_file builds the correct path."""
	result = _promote_winners.find_merged_file(
		"/fake/repo", 3, "amino_acids", 1
	)
	expected = os.path.join(
		"/fake/repo", "_staging", "merged",
		"ch03_amino_acids", "ch03_p01.pgml"
	)
	assert result == expected


#============================================
def test_find_merged_file_padding():
	"""Test zero-padding for chapter and problem numbers."""
	# chapter 3, problem 1 should become ch03_p01
	result = _promote_winners.find_merged_file(
		"/fake/repo", 3, "amino_acids", 1
	)
	assert "ch03_amino_acids" in result
	assert "ch03_p01.pgml" in result


#============================================
def test_build_dest_path():
	"""Test that build_dest_path constructs the output directory path."""
	result = _promote_winners.build_dest_path(
		"/fake/repo", 3, "amino_acids", 1
	)
	expected = os.path.join(
		"/fake/repo", "output",
		"ch03_amino_acids", "ch03_p01.pgml"
	)
	assert result == expected


#============================================
def test_load_referee_report(tmp_path):
	"""Test loading a valid referee report YAML file."""
	# create the expected directory structure
	report_dir = tmp_path / "reports" / "referee"
	report_dir.mkdir(parents=True)
	report_file = report_dir / "ch03_referee_report.yaml"
	report_data = {
		"slug": "amino_acids",
		"problems": [
			{"problem_num": 1, "action": "promote"},
			{"problem_num": 2, "action": "gap"},
		],
	}
	report_file.write_text(
		yaml.dump(report_data), encoding="utf-8"
	)
	# load and verify
	result = _promote_winners.load_referee_report(str(tmp_path), 3)
	assert result["slug"] == "amino_acids"
	assert len(result["problems"]) == 2
	assert result["problems"][0]["problem_num"] == 1


#============================================
def test_load_referee_report_missing(tmp_path):
	"""Test that loading a missing referee report raises FileNotFoundError."""
	with pytest.raises(FileNotFoundError):
		_promote_winners.load_referee_report(str(tmp_path), 99)


#============================================
def test_promote_file_wet(tmp_path):
	"""Test that promote_file copies the file when dry_run is False."""
	source = tmp_path / "source.pgml"
	source.write_text("DOCUMENT();\nENDDOCUMENT();\n")
	dest = tmp_path / "output" / "dest.pgml"
	result = _promote_winners.promote_file(
		str(source), str(dest), dry_run=False
	)
	assert result is True
	assert dest.exists()
	assert dest.read_text() == "DOCUMENT();\nENDDOCUMENT();\n"


#============================================
def test_promote_file_dry(tmp_path, capsys):
	"""Test that dry run prints a message but does not copy the file."""
	source = tmp_path / "source.pgml"
	source.write_text("test content")
	dest = tmp_path / "output" / "dest.pgml"
	result = _promote_winners.promote_file(
		str(source), str(dest), dry_run=True
	)
	assert result is True
	# dry run should not create the file
	assert not dest.exists()
	captured = capsys.readouterr()
	assert "dry-run" in captured.out


#============================================
def test_promote_file_creates_dirs(tmp_path):
	"""Test that promote_file creates missing destination directories."""
	source = tmp_path / "source.pgml"
	source.write_text("DOCUMENT();\nENDDOCUMENT();\n")
	# use a nested path that does not exist yet
	dest = tmp_path / "deep" / "nested" / "dir" / "dest.pgml"
	assert not dest.parent.exists()
	result = _promote_winners.promote_file(
		str(source), str(dest), dry_run=False
	)
	assert result is True
	assert dest.parent.exists()
	assert dest.exists()
	assert dest.read_text() == "DOCUMENT();\nENDDOCUMENT();\n"
