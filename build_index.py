#!/usr/bin/env python3

"""Build a concept index and coverage report from concepts YAML and generated PGML files."""

# Standard Library
import os
import glob
import argparse

# PIP3 modules
import yaml

#============================================
def load_concepts(concepts_dir: str) -> dict:
	"""Load all concept YAML files from the concepts directory.

	Args:
		concepts_dir: Path to directory containing ch{NN}_concepts.yaml files.

	Returns:
		Dict mapping chapter number (int) to list of concept dicts.
	"""
	concepts = {}
	# find all chapter concept YAML files
	pattern = os.path.join(concepts_dir, "ch*_concepts.yaml")
	yaml_files = sorted(glob.glob(pattern))
	for yaml_path in yaml_files:
		basename = os.path.basename(yaml_path)
		# extract chapter number from filename like ch01_concepts.yaml
		chapter_str = basename.split("_")[0].replace("ch", "")
		chapter_num = int(chapter_str)
		with open(yaml_path, "r") as f:
			data = yaml.safe_load(f)
		if data is None:
			data = []
		# handle both list format and dict-with-concepts-key format
		if isinstance(data, dict) and "concepts" in data:
			concept_list = data["concepts"]
		elif isinstance(data, list):
			concept_list = data
		else:
			concept_list = []
		concepts[chapter_num] = concept_list
	return concepts

#============================================
def scan_pgml_files(output_dir: str) -> dict:
	"""Scan output directory for generated PGML files.

	Args:
		output_dir: Path to output directory containing PGML files.

	Returns:
		Dict mapping chapter slug (str) to list of PGML file paths.
	"""
	pgml_files = {}
	# search recursively for .pgml files
	pattern = os.path.join(output_dir, "**", "*.pgml")
	found_files = sorted(glob.glob(pattern, recursive=True))
	for pgml_path in found_files:
		# derive chapter slug from the relative path
		rel_path = os.path.relpath(pgml_path, output_dir)
		parts = rel_path.split(os.sep)
		# use the top-level directory as the chapter slug
		if len(parts) > 1:
			chapter_slug = parts[0]
		else:
			# file is directly in output_dir
			chapter_slug = "ungrouped"
		if chapter_slug not in pgml_files:
			pgml_files[chapter_slug] = []
		pgml_files[chapter_slug].append(pgml_path)
	return pgml_files

#============================================
def build_concept_index(concepts: dict, pgml_files: dict) -> dict:
	"""Cross-reference concepts with generated PGML question files.

	Args:
		concepts: Dict from load_concepts (chapter_num -> concept list).
		pgml_files: Dict from scan_pgml_files (chapter_slug -> file list).

	Returns:
		Index dict suitable for YAML serialization.
	"""
	index = {}
	for chapter_num, concept_list in sorted(concepts.items()):
		chapter_key = f"chapter_{chapter_num:02d}"
		# look for matching pgml files by chapter number in slug
		matching_slugs = []
		for slug in pgml_files:
			# match slugs that contain the chapter number
			chapter_str = f"{chapter_num:02d}"
			if chapter_str in slug or f"ch{chapter_num}" in slug:
				matching_slugs.append(slug)
		# collect all matching pgml paths
		matched_pgml = []
		for slug in matching_slugs:
			matched_pgml.extend(pgml_files[slug])
		chapter_entry = {
			"chapter_number": chapter_num,
			"num_concepts": len(concept_list),
			"num_questions": len(matched_pgml),
			"concepts": [],
			"pgml_files": matched_pgml,
		}
		# add individual concept entries
		for concept in concept_list:
			if isinstance(concept, dict):
				concept_name = concept.get("name", concept.get("topic", "unknown"))
			else:
				concept_name = str(concept)
			chapter_entry["concepts"].append(concept_name)
		index[chapter_key] = chapter_entry
	return index

#============================================
def generate_coverage_report(concepts: dict, pgml_files: dict) -> str:
	"""Generate a text coverage report comparing concepts to generated questions.

	Args:
		concepts: Dict from load_concepts (chapter_num -> concept list).
		pgml_files: Dict from scan_pgml_files (chapter_slug -> file list).

	Returns:
		Report as a multi-line string.
	"""
	# count totals
	num_chapters = len(concepts)
	total_concepts = sum(len(cl) for cl in concepts.values())
	total_pgml = sum(len(fl) for fl in pgml_files.values())
	# find chapters with questions
	chapters_with_questions = 0
	concepts_with_questions = 0
	gaps = []
	for chapter_num, concept_list in sorted(concepts.items()):
		chapter_str = f"{chapter_num:02d}"
		# check if any pgml slug matches this chapter
		has_questions = False
		for slug in pgml_files:
			if chapter_str in slug or f"ch{chapter_num}" in slug:
				has_questions = True
				break
		if has_questions:
			chapters_with_questions += 1
			concepts_with_questions += len(concept_list)
		else:
			# all concepts in this chapter are gaps
			for concept in concept_list:
				if isinstance(concept, dict):
					concept_name = concept.get("name", concept.get("topic", "unknown"))
				else:
					concept_name = str(concept)
				gaps.append(f"  Chapter {chapter_num:02d}: {concept_name}")
	# build report lines
	report = ""
	report += "Coverage Report\n"
	report += "=" * 50 + "\n"
	report += "\n"
	report += "Summary Statistics\n"
	report += "-" * 30 + "\n"
	report += f"Chapters with concepts:    {num_chapters}\n"
	report += f"Chapters with questions:   {chapters_with_questions}\n"
	report += f"Total concepts defined:    {total_concepts}\n"
	report += f"Total PGML files found:    {total_pgml}\n"
	report += f"Concepts with questions:   {concepts_with_questions}\n"
	report += f"Concepts missing questions: {total_concepts - concepts_with_questions}\n"
	report += "\n"
	if gaps:
		report += "Gaps (concepts without questions)\n"
		report += "-" * 40 + "\n"
		for gap_line in gaps:
			report += gap_line + "\n"
	else:
		report += "No gaps found. All concepts have questions.\n"
	return report

#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Build concept index and coverage report from YAML and PGML files."
	)
	parser.add_argument(
		'-c', '--concepts-dir', dest='concepts_dir',
		default='concepts',
		help='Directory containing concept YAML files (default: concepts)',
	)
	parser.add_argument(
		'-o', '--output-dir', dest='output_dir',
		default='output',
		help='Directory containing generated PGML files (default: output)',
	)
	parser.add_argument(
		'-r', '--reports-dir', dest='reports_dir',
		default='reports',
		help='Directory for output reports (default: reports)',
	)
	args = parser.parse_args()
	return args

#============================================
def main():
	"""Orchestrate concept index building and coverage reporting."""
	args = parse_args()
	# ensure output directories exist
	os.makedirs(args.output_dir, exist_ok=True)
	os.makedirs(args.reports_dir, exist_ok=True)
	# load data
	concepts = load_concepts(args.concepts_dir)
	pgml_files = scan_pgml_files(args.output_dir)
	# build index and write YAML
	index = build_concept_index(concepts, pgml_files)
	index_path = os.path.join(args.output_dir, "concept_index.yaml")
	with open(index_path, "w") as f:
		yaml.dump(index, f, default_flow_style=False, sort_keys=False)
	print(f"Wrote concept index: {index_path}")
	# generate coverage report and write text file
	report = generate_coverage_report(concepts, pgml_files)
	report_path = os.path.join(args.reports_dir, "coverage_report.txt")
	with open(report_path, "w") as f:
		f.write(report)
	print(f"Wrote coverage report: {report_path}")
	# also print report to stdout
	print()
	print(report)

#============================================
if __name__ == '__main__':
	main()
