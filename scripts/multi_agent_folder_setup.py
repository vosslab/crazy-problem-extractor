#!/usr/bin/env python3
"""Manifest builder and coder dispatch for the chaotic PGML pipeline.

Reads chapter JSON files, builds problem manifests, creates staging
directories, and assigns problems to coders using modular assignment.
"""

# Standard Library
import os
import glob
import argparse

import yaml


#============================================
def extract_slug(filename: str, prefix: str = "ch") -> str:
	"""Extract the chapter slug from a JSON filename.

	Args:
		filename: Filename like 'ch03_amino_acids.json' or
			'bio2e_ch05_the_structure_of_cells.json'.
		prefix: Prefix before the chapter number (default: 'ch').

	Returns:
		The slug portion (e.g. 'amino_acids').
	"""
	# strip directory component if present
	base = os.path.basename(filename)
	# remove .json extension
	name = base.rsplit(".", 1)[0]
	# remove prefix + NN_ pattern
	# find the prefix, skip digits, skip underscore
	idx = name.find(prefix)
	if idx < 0:
		return name
	# skip past prefix
	rest = name[idx + len(prefix):]
	# skip past digits
	i = 0
	while i < len(rest) and rest[i].isdigit():
		i += 1
	# skip past underscore separator
	if i < len(rest) and rest[i] == '_':
		i += 1
	slug = rest[i:]
	return slug


#============================================
def find_chapter_json(repo_root: str, chapter_num: int, prefix: str = "ch") -> str:
	"""Find the JSON file for a chapter in structured/chapters/.

	Args:
		repo_root: Path to the repository root.
		chapter_num: Chapter number.
		prefix: Filename prefix (default: 'ch').

	Returns:
		Path to the chapter JSON file.

	Raises:
		FileNotFoundError: If no matching file is found.
	"""
	chapters_dir = os.path.join(repo_root, "structured", "chapters")
	ch_padded = f"{prefix}{chapter_num:02d}"
	# glob for matching files
	pattern = os.path.join(chapters_dir, f"{ch_padded}_*.json")
	matches = glob.glob(pattern)
	if not matches:
		raise FileNotFoundError(
			f"No chapter JSON found matching {pattern}"
		)
	# return the first match (should be unique)
	return matches[0]


#============================================
def build_manifest(chapter_data: dict, slug: str, include_all: bool = False) -> dict:
	"""Build a problem manifest from chapter data.

	Only includes problems that have answers, unless include_all is True.
	Deduplicates by problem number, keeping the first entry.

	Args:
		chapter_data: Parsed chapter JSON dict.
		slug: Chapter slug.
		include_all: If True, include all problems regardless of answers.

	Returns:
		Manifest dict with chapter_num, title, slug, and problems list.
	"""
	chapter_num = chapter_data["chapter_num"]
	title = chapter_data.get("title", "")
	answers = chapter_data.get("answers", {})
	problems = []
	seen_numbers = set()
	# collect standard problems
	for prob in chapter_data.get("problems", []):
		num = prob["number"]
		if num in seen_numbers:
			continue
		# check if answer exists (keys may be strings)
		has_answer = str(num) in answers or num in answers
		if not include_all and not has_answer:
			continue
		seen_numbers.add(num)
		entry = {
			"number": num,
			"text": prob.get("text", ""),
			"answer": answers.get(str(num), answers.get(num, "")),
			"type": "standard",
		}
		problems.append(entry)
	# collect challenge problems
	for prob in chapter_data.get("challenge_problems", []):
		num = prob["number"]
		if num in seen_numbers:
			continue
		has_answer = str(num) in answers or num in answers
		if not include_all and not has_answer:
			continue
		seen_numbers.add(num)
		entry = {
			"number": num,
			"text": prob.get("text", ""),
			"answer": answers.get(str(num), answers.get(num, "")),
			"type": "challenge",
		}
		problems.append(entry)
	# sort by problem number
	problems.sort(key=lambda p: p["number"])
	manifest = {
		"chapter_num": chapter_num,
		"title": title,
		"slug": slug,
		"problems": problems,
	}
	return manifest


#============================================
def create_staging_dirs(
	repo_root: str, chapter_num: int, slug: str,
	num_coders: int, prefix: str = "ch",
) -> list:
	"""Create staging directories for coders and merged output.

	Args:
		repo_root: Path to the repository root.
		chapter_num: Chapter number.
		slug: Chapter slug.
		num_coders: Number of coder directories to create.
		prefix: Directory name prefix (default: 'ch').

	Returns:
		List of created directory paths (coder dirs + merged dir).
	"""
	ch_padded = f"{prefix}{chapter_num:02d}"
	chapter_dirname = f"{ch_padded}_{slug}"
	staging_dir = os.path.join(repo_root, "_staging")
	dirs = []
	# create coder directories
	for i in range(1, num_coders + 1):
		coder_dir = os.path.join(staging_dir, f"coder_{i}", chapter_dirname)
		os.makedirs(coder_dir, exist_ok=True)
		dirs.append(coder_dir)
	# create merged directory
	merged_dir = os.path.join(staging_dir, "merged", chapter_dirname)
	os.makedirs(merged_dir, exist_ok=True)
	dirs.append(merged_dir)
	return dirs


#============================================
def write_manifest(
	repo_root: str, chapter_num: int, manifest: dict,
	prefix: str = "ch",
) -> str:
	"""Write a manifest dict to YAML in _staging/.

	Args:
		repo_root: Path to the repository root.
		chapter_num: Chapter number.
		manifest: Manifest dict to serialize.
		prefix: Filename prefix (default: 'ch').

	Returns:
		Path to the written manifest file.
	"""
	ch_padded = f"{prefix}{chapter_num:02d}"
	staging_dir = os.path.join(repo_root, "_staging")
	os.makedirs(staging_dir, exist_ok=True)
	manifest_path = os.path.join(staging_dir, f"{ch_padded}_manifest.yaml")
	with open(manifest_path, "w", encoding="utf-8") as f:
		yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
	return manifest_path


#============================================
def assign_problems_modular(problem_numbers: list, num_coders: int) -> dict:
	"""Assign problems to coders using modular assignment.

	Each problem goes to coder (index % num_coders) + 1.
	All non-required problems become optional for each coder.

	Args:
		problem_numbers: Sorted list of problem numbers.
		num_coders: Number of coders.

	Returns:
		Dict mapping coder_num -> {'required': [...], 'optional': [...]}.
	"""
	# sort problem numbers
	sorted_problems = sorted(problem_numbers)
	# initialize assignments
	assignments = {}
	for c in range(1, num_coders + 1):
		assignments[c] = {"required": [], "optional": []}
	# assign by index
	for idx, prob_num in enumerate(sorted_problems):
		coder = (idx % num_coders) + 1
		assignments[coder]["required"].append(prob_num)
	# fill optional lists with all non-required problems
	all_problems = set(sorted_problems)
	for c in range(1, num_coders + 1):
		required_set = set(assignments[c]["required"])
		assignments[c]["optional"] = sorted(all_problems - required_set)
	return assignments


#============================================
def write_assignments(
	repo_root: str, chapter_num: int, slug: str,
	assignments: dict, prefix: str = "ch",
) -> list:
	"""Write per-coder assignment YAML files.

	Args:
		repo_root: Path to the repository root.
		chapter_num: Chapter number.
		slug: Chapter slug.
		assignments: Dict from assign_problems_modular().
		prefix: Directory name prefix (default: 'ch').

	Returns:
		List of paths to written assignment files.
	"""
	ch_padded = f"{prefix}{chapter_num:02d}"
	chapter_dirname = f"{ch_padded}_{slug}"
	staging_dir = os.path.join(repo_root, "_staging")
	paths = []
	for coder_num in sorted(assignments.keys()):
		coder_dir = os.path.join(
			staging_dir, f"coder_{coder_num}", chapter_dirname
		)
		os.makedirs(coder_dir, exist_ok=True)
		assignment_path = os.path.join(coder_dir, "assignments.yaml")
		with open(assignment_path, "w", encoding="utf-8") as f:
			yaml.dump(
				assignments[coder_num], f,
				default_flow_style=False, sort_keys=False,
			)
		paths.append(assignment_path)
	return paths


#============================================
def print_assignment_summary(assignments: dict) -> None:
	"""Print a human-readable assignment summary.

	Args:
		assignments: Dict from assign_problems_modular().
	"""
	for coder_num in sorted(assignments.keys()):
		req = assignments[coder_num]["required"]
		opt = assignments[coder_num]["optional"]
		req_str = ", ".join(f"p{n:02d}" for n in req)
		print(f"  Coder {coder_num}: required [{req_str}] + {len(opt)} optional")


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Build problem manifest and dispatch coders"
	)
	parser.add_argument(
		'-c', '--chapter', dest='chapter_num', type=int, required=True,
		help="Chapter number to dispatch"
	)
	parser.add_argument(
		'-k', '--coders', dest='num_coders', type=int, default=2,
		help="Number of coder slots to create (default: 2)"
	)
	parser.add_argument(
		'-p', '--prefix', dest='prefix', type=str, default='ch',
		help="Chapter prefix (default: 'ch', use 'bio2e_ch' for Biology 2e)"
	)
	# assignment mode
	assign_group = parser.add_mutually_exclusive_group()
	assign_group.add_argument(
		'-a', '--assign', dest='assign_mode', type=str,
		choices=('none', 'modular'), default='modular',
		help="Assignment strategy (default: modular)"
	)
	# include-all flag
	parser.add_argument(
		'--include-all', dest='include_all', action='store_true',
		help="Include problems without answers"
	)
	parser.set_defaults(include_all=False)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Main entry point."""
	args = parse_args()
	repo_root = os.path.dirname(os.path.abspath(__file__))
	# find and load chapter JSON
	json_path = find_chapter_json(repo_root, args.chapter_num, prefix=args.prefix)
	print(f"Found chapter JSON: {json_path}")
	with open(json_path, "r", encoding="utf-8") as f:
		import json
		chapter_data = json.load(f)
	# extract slug
	slug = extract_slug(os.path.basename(json_path), prefix=args.prefix)
	print(f"Chapter {args.chapter_num}: {slug}")
	# build manifest
	manifest = build_manifest(chapter_data, slug, include_all=args.include_all)
	print(f"  {len(manifest['problems'])} problems in manifest")
	# write manifest
	manifest_path = write_manifest(
		repo_root, args.chapter_num, manifest, prefix=args.prefix
	)
	print(f"  Manifest written to {manifest_path}")
	# create staging directories
	dirs = create_staging_dirs(
		repo_root, args.chapter_num, slug, args.num_coders, prefix=args.prefix
	)
	print(f"  Created {len(dirs)} staging directories")
	# assign problems if requested
	if args.assign_mode == "modular" and manifest["problems"]:
		problem_numbers = [p["number"] for p in manifest["problems"]]
		assignments = assign_problems_modular(problem_numbers, args.num_coders)
		paths = write_assignments(
			repo_root, args.chapter_num, slug, assignments, prefix=args.prefix
		)
		print(f"  Wrote {len(paths)} assignment files")
		print_assignment_summary(assignments)


if __name__ == '__main__':
	main()
