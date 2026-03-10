#!/usr/bin/env python3

"""Builds reusable template blocks for WeBWorK PGML problem files."""

#============================================
def build_header_block(
	title: str,
	description: str,
	keywords: str,
	db_subject: str,
	db_chapter: str,
	db_section: str,
	level: int,
	author: str,
	institution: str,
) -> str:
	"""Build a valid OPL header block for a WeBWorK .pgml file.

	Args:
		title: title text for the problem
		description: short description of the problem
		keywords: comma-separated keywords string
		db_subject: OPL subject classification
		db_chapter: OPL chapter classification
		db_section: OPL section classification
		level: difficulty level (1-5)
		author: problem author name
		institution: author institution abbreviation

	Returns:
		A multiline string containing the OPL header comment block.
	"""
	# build list of header lines in OPL format
	lines = []
	lines.append(f"## DBsubject({db_subject})")
	lines.append(f"## DBchapter({db_chapter})")
	lines.append(f"## DBsection({db_section})")
	lines.append(f"## Level({level})")
	lines.append(f"## KEYWORDS('{keywords}')")
	lines.append(f"## TitleText1('{title}')")
	lines.append(f"## AuthorText1('{author}')")
	lines.append(f"## Author({author})")
	lines.append(f"## Institution({institution})")
	# join all header lines with newlines
	header_text = "\n".join(lines)
	return header_text

#============================================
def build_preamble(macros: list) -> str:
	"""Build the DOCUMENT() and loadMacros block for a PGML file.

	Always includes PGstandard.pl and PGML.pl in the macro list.
	Uses PGrandom->new() with separate srand($problemSeed) call.
	Includes Context("Numeric") after loadMacros.
	Omits TEXT(beginproblem()) since ADAPT handles it.

	Args:
		macros: list of additional macro filenames to load

	Returns:
		A multiline string containing the preamble block.
	"""
	# ensure required macros are always present
	required = ["PGstandard.pl", "PGML.pl"]
	all_macros = list(required)
	for macro in macros:
		# skip duplicates of required macros
		if macro not in all_macros:
			all_macros.append(macro)

	# build the loadMacros argument list
	macro_lines = ""
	for macro in all_macros:
		macro_lines += f'\t"{macro}",\n'

	# assemble the full preamble
	preamble = "DOCUMENT();\n"
	preamble += "loadMacros(\n"
	preamble += macro_lines
	preamble += ");\n"
	preamble += 'Context("Numeric");\n'
	preamble += "$rng = PGrandom->new();\n"
	preamble += "$rng->srand($problemSeed);"
	return preamble

#============================================
def build_solution_block(explanation: str) -> str:
	"""Build a PGML solution block.

	Args:
		explanation: the solution explanation text

	Returns:
		A multiline string containing the PGML solution block.
	"""
	solution = "BEGIN_PGML_SOLUTION\n"
	solution += explanation + "\n"
	solution += "END_PGML_SOLUTION"
	return solution

#============================================
def build_footer() -> str:
	"""Build the closing ENDDOCUMENT line for a PGML file.

	Returns:
		The ENDDOCUMENT(); string.
	"""
	return "ENDDOCUMENT();"

#============================================
def main() -> None:
	"""Run assertion tests for all template builder functions."""
	# test build_header_block produces expected OPL lines
	header = build_header_block(
		title="Biochemistry: A Short Course",
		description="amino acid identification",
		keywords="amino acids",
		db_subject="Biology",
		db_chapter="Biochemistry",
		db_section="Amino Acids",
		level=2,
		author="Neil Voss",
		institution="NSH",
	)
	assert "## DBsubject(Biology)" in header
	assert "## DBchapter(Biochemistry)" in header
	assert "## DBsection(Amino Acids)" in header
	assert "## Level(2)" in header
	assert "## Author(Neil Voss)" in header
	assert "## Institution(NSH)" in header

	# test build_preamble includes required elements
	preamble = build_preamble(["parserRadioButtons.pl"])
	assert "DOCUMENT();" in preamble
	assert "loadMacros(" in preamble
	assert '"PGstandard.pl"' in preamble
	assert '"PGML.pl"' in preamble
	assert '"parserRadioButtons.pl"' in preamble
	assert 'Context("Numeric");' in preamble
	assert "$rng = PGrandom->new();" in preamble
	assert "$rng->srand($problemSeed);" in preamble

	# test build_preamble deduplicates required macros
	preamble2 = build_preamble(["PGstandard.pl", "PGML.pl", "extra.pl"])
	# count occurrences of PGstandard.pl
	count = preamble2.count("PGstandard.pl")
	assert count == 1, f"PGstandard.pl appeared {count} times, expected 1"

	# test build_solution_block wraps explanation
	solution = build_solution_block("This is the explanation.")
	assert "BEGIN_PGML_SOLUTION" in solution
	assert "This is the explanation." in solution
	assert "END_PGML_SOLUTION" in solution

	# test build_footer returns correct closing
	footer = build_footer()
	assert footer == "ENDDOCUMENT();"

	print("All assertions passed.")

#============================================
if __name__ == "__main__":
	main()
