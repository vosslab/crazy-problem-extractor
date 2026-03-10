#!/usr/bin/env python3

"""Tests for build_index module."""

# Standard Library
import os
import sys

import pytest

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import build_index


#============================================
class TestLoadConcepts:
	"""Tests for load_concepts function."""

	#============================================
	def test_load_list_format(self, tmp_path):
		"""Test loading YAML with list format."""
		# create a concept yaml file in list format
		yaml_content = (
			"- name: protein folding\n"
			"  topic: biochemistry\n"
			"- name: enzyme kinetics\n"
			"  topic: biochemistry\n"
		)
		yaml_file = tmp_path / "ch01_concepts.yaml"
		yaml_file.write_text(yaml_content, encoding="utf-8")
		concepts = build_index.load_concepts(str(tmp_path))
		assert 1 in concepts
		assert len(concepts[1]) == 2

	#============================================
	def test_load_dict_format(self, tmp_path):
		"""Test loading YAML with dict-with-concepts-key format."""
		yaml_content = (
			"concepts:\n"
			"  - name: amino acids\n"
			"  - name: peptide bonds\n"
		)
		yaml_file = tmp_path / "ch02_concepts.yaml"
		yaml_file.write_text(yaml_content, encoding="utf-8")
		concepts = build_index.load_concepts(str(tmp_path))
		assert 2 in concepts
		assert len(concepts[2]) == 2

	#============================================
	def test_load_empty_yaml(self, tmp_path):
		"""Test loading empty YAML file returns empty list."""
		yaml_file = tmp_path / "ch03_concepts.yaml"
		yaml_file.write_text("", encoding="utf-8")
		concepts = build_index.load_concepts(str(tmp_path))
		assert 3 in concepts
		assert len(concepts[3]) == 0

	#============================================
	def test_load_no_files(self, tmp_path):
		"""Test loading from directory with no concept files."""
		concepts = build_index.load_concepts(str(tmp_path))
		assert len(concepts) == 0

	#============================================
	def test_load_multiple_chapters(self, tmp_path):
		"""Test loading multiple chapter files."""
		for ch_num in (1, 5, 12):
			yaml_content = f"- name: concept_{ch_num}\n"
			yaml_file = tmp_path / f"ch{ch_num:02d}_concepts.yaml"
			yaml_file.write_text(yaml_content, encoding="utf-8")
		concepts = build_index.load_concepts(str(tmp_path))
		assert len(concepts) == 3
		assert 1 in concepts
		assert 5 in concepts
		assert 12 in concepts


#============================================
class TestScanPgmlFiles:
	"""Tests for scan_pgml_files function."""

	#============================================
	def test_scan_empty_directory(self, tmp_path):
		"""Test scanning empty directory."""
		result = build_index.scan_pgml_files(str(tmp_path))
		assert len(result) == 0

	#============================================
	def test_scan_with_chapter_dirs(self, tmp_path):
		"""Test scanning with chapter subdirectories."""
		ch01_dir = tmp_path / "ch01"
		ch01_dir.mkdir()
		pgml_file = ch01_dir / "q1.pgml"
		pgml_file.write_text("DOCUMENT();\nENDDOCUMENT();\n", encoding="utf-8")
		result = build_index.scan_pgml_files(str(tmp_path))
		assert "ch01" in result
		assert len(result["ch01"]) == 1

	#============================================
	def test_scan_ungrouped_files(self, tmp_path):
		"""Test that files directly in output_dir get ungrouped slug."""
		pgml_file = tmp_path / "q1.pgml"
		pgml_file.write_text("DOCUMENT();\n", encoding="utf-8")
		result = build_index.scan_pgml_files(str(tmp_path))
		assert "ungrouped" in result

	#============================================
	def test_scan_multiple_chapters(self, tmp_path):
		"""Test scanning multiple chapter directories."""
		for ch in ("ch01", "ch02"):
			ch_dir = tmp_path / ch
			ch_dir.mkdir()
			pgml_file = ch_dir / "q1.pgml"
			pgml_file.write_text("DOCUMENT();\n", encoding="utf-8")
		result = build_index.scan_pgml_files(str(tmp_path))
		assert "ch01" in result
		assert "ch02" in result


#============================================
class TestBuildConceptIndex:
	"""Tests for build_concept_index function."""

	#============================================
	def test_basic_index(self):
		"""Test building index from simple concepts and pgml_files."""
		concepts = {
			1: [{"name": "protein folding"}, {"name": "enzyme kinetics"}],
		}
		pgml_files = {
			"ch01": ["/out/ch01/q1.pgml", "/out/ch01/q2.pgml"],
		}
		index = build_index.build_concept_index(concepts, pgml_files)
		assert "chapter_01" in index
		entry = index["chapter_01"]
		assert entry["chapter_number"] == 1
		assert entry["num_concepts"] == 2
		assert entry["num_questions"] == 2
		assert "protein folding" in entry["concepts"]
		assert "enzyme kinetics" in entry["concepts"]

	#============================================
	def test_no_matching_pgml(self):
		"""Test index when no pgml files match a chapter."""
		concepts = {
			3: [{"name": "gene expression"}],
		}
		pgml_files = {}
		index = build_index.build_concept_index(concepts, pgml_files)
		assert "chapter_03" in index
		entry = index["chapter_03"]
		assert entry["num_questions"] == 0

	#============================================
	def test_string_concepts(self):
		"""Test index with plain string concepts (not dicts)."""
		concepts = {
			1: ["amino acids", "peptide bonds"],
		}
		pgml_files = {}
		index = build_index.build_concept_index(concepts, pgml_files)
		entry = index["chapter_01"]
		assert "amino acids" in entry["concepts"]
		assert "peptide bonds" in entry["concepts"]

	#============================================
	def test_empty_inputs(self):
		"""Test index with empty concepts and pgml_files."""
		index = build_index.build_concept_index({}, {})
		assert len(index) == 0


#============================================
class TestGenerateCoverageReport:
	"""Tests for generate_coverage_report function."""

	#============================================
	def test_report_structure(self):
		"""Test report contains expected sections."""
		concepts = {
			1: [{"name": "topic_a"}, {"name": "topic_b"}],
		}
		pgml_files = {
			"ch01": ["/out/ch01/q1.pgml"],
		}
		report = build_index.generate_coverage_report(concepts, pgml_files)
		assert "Coverage Report" in report
		assert "Summary Statistics" in report
		assert "Chapters with concepts:" in report
		assert "Total concepts defined:" in report

	#============================================
	def test_report_with_gaps(self):
		"""Test report shows gaps when chapters have no questions."""
		concepts = {
			1: [{"name": "topic_a"}],
			2: [{"name": "topic_b"}],
		}
		# only chapter 1 has questions
		pgml_files = {
			"ch01": ["/out/ch01/q1.pgml"],
		}
		report = build_index.generate_coverage_report(concepts, pgml_files)
		assert "Gaps" in report
		assert "Chapter 02" in report

	#============================================
	def test_report_no_gaps(self):
		"""Test report when all chapters have questions."""
		concepts = {
			1: [{"name": "topic_a"}],
		}
		pgml_files = {
			"ch01": ["/out/ch01/q1.pgml"],
		}
		report = build_index.generate_coverage_report(concepts, pgml_files)
		assert "No gaps found" in report

	#============================================
	def test_report_empty_inputs(self):
		"""Test report with no concepts or files."""
		report = build_index.generate_coverage_report({}, {})
		assert "Coverage Report" in report
		assert "Chapters with concepts:    0" in report

	#============================================
	def test_report_returns_string(self):
		"""Test that report returns a string type."""
		report = build_index.generate_coverage_report({}, {})
		assert isinstance(report, str)
