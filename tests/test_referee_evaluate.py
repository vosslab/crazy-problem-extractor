"""Tests for _referee_evaluate module pure functions."""

# Standard Library
import os
import sys
import unittest.mock

import pytest

import yaml

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import _referee_evaluate


#============================================
class TestLoadManifest:
	"""Tests for load_manifest function."""

	#============================================
	def test_load_manifest(self, tmp_path):
		"""Test loading a valid manifest YAML file."""
		# create the _staging directory and a manifest file
		staging_dir = tmp_path / "_staging"
		staging_dir.mkdir()
		manifest_data = {
			"chapter_num": 3,
			"slug": "amino_acids",
			"problems": [
				{"number": 1, "text": "What is glycine?", "answer": "simplest amino acid", "type": "standard"},
				{"number": 2, "text": "What is alanine?", "answer": "nonpolar amino acid", "type": "standard"},
			],
		}
		manifest_path = staging_dir / "ch03_manifest.yaml"
		with open(str(manifest_path), "w", encoding="utf-8") as f:
			yaml.dump(manifest_data, f, default_flow_style=False)
		# load and verify
		result = _referee_evaluate.load_manifest(str(tmp_path), 3)
		assert result["chapter_num"] == 3
		assert result["slug"] == "amino_acids"
		assert len(result["problems"]) == 2
		assert result["problems"][0]["number"] == 1
		assert result["problems"][1]["number"] == 2

	#============================================
	def test_load_manifest_missing(self, tmp_path):
		"""Test that loading a missing manifest raises FileNotFoundError."""
		# create _staging dir but no manifest file
		staging_dir = tmp_path / "_staging"
		staging_dir.mkdir()
		with pytest.raises(FileNotFoundError):
			_referee_evaluate.load_manifest(str(tmp_path), 99)


#============================================
class TestScanStagingFiles:
	"""Tests for scan_staging_files function."""

	#============================================
	def test_scan_staging_files(self, tmp_path):
		"""Test scanning staging dirs groups PGML files by problem number."""
		# minimal PGML content for fake files
		pgml_content = "DOCUMENT();\nENDDOCUMENT();\n"
		# create coder_1 directory with problems 1 and 5
		coder1_dir = tmp_path / "_staging" / "coder_1" / "ch03_amino_acids"
		coder1_dir.mkdir(parents=True)
		p01_coder1 = coder1_dir / "ch03_p01.pgml"
		p01_coder1.write_text(pgml_content, encoding="utf-8")
		p05_coder1 = coder1_dir / "ch03_p05.pgml"
		p05_coder1.write_text(pgml_content, encoding="utf-8")
		# create coder_2 directory with problem 1
		coder2_dir = tmp_path / "_staging" / "coder_2" / "ch03_amino_acids"
		coder2_dir.mkdir(parents=True)
		p01_coder2 = coder2_dir / "ch03_p01.pgml"
		p01_coder2.write_text(pgml_content, encoding="utf-8")
		# scan and verify grouping
		result = _referee_evaluate.scan_staging_files(str(tmp_path), 3, "amino_acids")
		# problem 1 should have 2 entries (coder_1 and coder_2)
		assert 1 in result
		assert len(result[1]) == 2
		# problem 5 should have 1 entry (coder_1 only)
		assert 5 in result
		assert len(result[5]) == 1
		# verify coder numbers are extracted correctly
		coder_nums_p1 = sorted([entry[0] for entry in result[1]])
		assert coder_nums_p1 == [1, 2]

	#============================================
	def test_scan_staging_files_empty(self, tmp_path):
		"""Test scanning staging dirs with no PGML files returns empty dict."""
		# create empty staging structure
		staging_dir = tmp_path / "_staging" / "coder_1" / "ch03_amino_acids"
		staging_dir.mkdir(parents=True)
		result = _referee_evaluate.scan_staging_files(str(tmp_path), 3, "amino_acids")
		assert result == {}


#============================================
class TestBuildReport:
	"""Tests for build_report function."""

	#============================================
	def test_build_report_gaps(self):
		"""Test that manifest problems with no staged files are all gaps."""
		manifest = {
			"chapter_num": 3,
			"slug": "amino_acids",
			"problems": [
				{"number": 1, "text": "q1", "answer": "a1", "type": "standard"},
				{"number": 2, "text": "q2", "answer": "a2", "type": "standard"},
				{"number": 3, "text": "q3", "answer": "a3", "type": "standard"},
			],
		}
		# no staged files at all
		staged_files = {}
		# mock validate_staged_file since build_report calls it internally
		with unittest.mock.patch.object(
			_referee_evaluate, "validate_staged_file", return_value=(0, 0)
		):
			report = _referee_evaluate.build_report(manifest, staged_files, "/fake/root")
		# verify all three problems are gaps
		assert report["chapter"] == 3
		assert report["slug"] == "amino_acids"
		assert len(report["problems"]) == 3
		for entry in report["problems"]:
			assert entry["action"] == "gap"
			assert entry["competing_versions"] == 0
			assert entry["versions"] == []
		# verify summary counts
		summary = report["summary"]
		assert summary["gaps"] == 3
		assert summary["singles"] == 0
		assert summary["competitions"] == 0
		assert summary["problems_covered"] == 0
		assert summary["total_problems"] == 3

	#============================================
	def test_build_report_mixed(self):
		"""Test report with a mix of gaps, singles, and competitions."""
		manifest = {
			"chapter_num": 3,
			"slug": "amino_acids",
			"problems": [
				{"number": 1, "text": "q1", "answer": "a1", "type": "standard"},
				{"number": 2, "text": "q2", "answer": "a2", "type": "standard"},
				{"number": 3, "text": "q3", "answer": "a3", "type": "standard"},
			],
		}
		# problem 1: two coders (competition), problem 2: one coder (single), problem 3: gap
		staged_files = {
			1: [
				(1, "/fake/root/_staging/coder_1/ch03_amino_acids/ch03_p01.pgml"),
				(2, "/fake/root/_staging/coder_2/ch03_amino_acids/ch03_p01.pgml"),
			],
			2: [
				(1, "/fake/root/_staging/coder_1/ch03_amino_acids/ch03_p02.pgml"),
			],
		}
		# mock validate_staged_file to return zero errors and warnings
		with unittest.mock.patch.object(
			_referee_evaluate, "validate_staged_file", return_value=(0, 0)
		):
			report = _referee_evaluate.build_report(manifest, staged_files, "/fake/root")
		# check per-problem actions
		actions = {entry["problem_num"]: entry["action"] for entry in report["problems"]}
		assert actions[1] == "competition"
		assert actions[2] == "single"
		assert actions[3] == "gap"
		# check version counts
		version_counts = {entry["problem_num"]: entry["competing_versions"] for entry in report["problems"]}
		assert version_counts[1] == 2
		assert version_counts[2] == 1
		assert version_counts[3] == 0
		# check summary
		summary = report["summary"]
		assert summary["gaps"] == 1
		assert summary["singles"] == 1
		assert summary["competitions"] == 1
		assert summary["problems_covered"] == 2
		assert summary["total_problems"] == 3


#============================================
class TestWriteReport:
	"""Tests for write_report function."""

	#============================================
	def test_write_report(self, tmp_path):
		"""Test writing a report to YAML and verifying its content."""
		report = {
			"chapter": 3,
			"slug": "amino_acids",
			"date": "2026-03-06",
			"problems": [
				{
					"problem_num": 1,
					"competing_versions": 1,
					"versions": [{"coder": 1, "file": "path/to/file.pgml", "errors": 0, "warnings": 0}],
					"action": "single",
				},
			],
			"summary": {
				"total_problems": 1,
				"problems_covered": 1,
				"gaps": 0,
				"competitions": 0,
				"singles": 1,
			},
		}
		# write the report
		report_path = _referee_evaluate.write_report(str(tmp_path), 3, report)
		# verify file was created
		assert os.path.isfile(report_path)
		# verify filename convention
		assert report_path.endswith("ch03_referee_report.yaml")
		# verify directory structure
		assert os.path.join("reports", "referee") in report_path
		# load written YAML and verify content
		with open(report_path, "r", encoding="utf-8") as f:
			loaded = yaml.safe_load(f)
		assert loaded["chapter"] == 3
		assert loaded["slug"] == "amino_acids"
		assert loaded["date"] == "2026-03-06"
		assert len(loaded["problems"]) == 1
		assert loaded["problems"][0]["action"] == "single"
		assert loaded["summary"]["singles"] == 1
		assert loaded["summary"]["gaps"] == 0
