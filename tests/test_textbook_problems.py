"""Pytest tests for textbook_problems module."""

import sys

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import textbook_problems


#============================================
def test_extract_problems_basic():
	"""Extract two numbered problems from a PROBLEMS section."""
	lines = [
		"PROBLEMS",
		"",
		"1.  First problem. What is the answer?",
		"",
		"2.  Second problem. Describe the thing",
		"that continues on this line.",
		"",
		"Challenge Problems",
		"3.  Hard one. Explain why.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 2
	assert problems[0]["number"] == 1
	assert "First problem" in problems[0]["text"]
	assert problems[1]["number"] == 2
	assert "continues on this line" in problems[1]["text"]


#============================================
def test_extract_problems_stops_at_challenge():
	"""Problems section stops when Challenge Problems heading appears."""
	lines = [
		"PROBLEMS",
		"1.  Only problem.",
		"Challenge Problems",
		"2.  This is a challenge.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 1
	assert problems[0]["number"] == 1


#============================================
def test_extract_problems_stops_at_selected_readings():
	"""Problems section stops at Selected Readings heading."""
	lines = [
		"PROBLEMS",
		"1.  Problem one. Text here.",
		"Selected Readings for this chapter",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 1
	assert problems[0]["number"] == 1


#============================================
def test_extract_problems_stops_at_data_interpretation():
	"""Problems section stops at Data Interpretation Problems heading."""
	lines = [
		"PROBLEMS",
		"1.  Problem one. Text.",
		"2.  Problem two. More text.",
		"Data Interpretation Problems",
		"3.  DI problem.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 2


#============================================
def test_extract_problems_multiline():
	"""Multi-line problem text is joined into a single string."""
	lines = [
		"PROBLEMS",
		"1.  This is a problem that spans",
		"multiple lines and should be",
		"joined together.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 1
	text = problems[0]["text"]
	assert "spans" in text
	assert "joined together" in text
	# verify multiple spaces are collapsed
	assert "  " not in text


#============================================
def test_extract_problems_blank_lines_between():
	"""Blank lines between continuation lines do not split a problem."""
	lines = [
		"PROBLEMS",
		"1.  Start of problem.",
		"",
		"Still part of problem one.",
		"",
		"2.  Second problem.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 2
	assert "Still part of problem one" in problems[0]["text"]


#============================================
def test_extract_problems_empty_input():
	"""Empty input returns an empty list."""
	result = textbook_problems.extract_problems([])
	assert result == []


#============================================
def test_extract_problems_no_heading():
	"""Lines without PROBLEMS heading return empty list."""
	lines = ["Some random text", "No heading here"]
	result = textbook_problems.extract_problems(lines)
	assert result == []


#============================================
def test_extract_problems_stops_at_chapter_header():
	"""Problems section stops at a chapter header pattern."""
	lines = [
		"PROBLEMS",
		"1.  A problem.",
		"C h a p t e r  5",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 1


#============================================
def test_extract_problems_stops_at_answers_to():
	"""Problems section stops at Answers to heading."""
	lines = [
		"PROBLEMS",
		"1.  Problem text.",
		"Answers to Self-Assessment Questions",
	]
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 1


#============================================
def test_extract_challenge_problems_basic():
	"""Extract challenge problems from the Challenge Problems section."""
	lines = [
		"PROBLEMS",
		"1.  Regular problem.",
		"Challenge Problems",
		"2.  Hard problem. Why does this happen?",
		"3.  Another hard one.",
		"Selected Readings for this chapter",
	]
	challenge = textbook_problems.extract_challenge_problems(lines)
	assert len(challenge) == 2
	assert challenge[0]["number"] == 2
	assert challenge[1]["number"] == 3


#============================================
def test_extract_challenge_problems_singular_heading():
	"""Singular Challenge Problem heading is also recognized."""
	lines = [
		"Challenge Problem",
		"5.  The only challenge. Solve it.",
	]
	challenge = textbook_problems.extract_challenge_problems(lines)
	assert len(challenge) == 1
	assert challenge[0]["number"] == 5


#============================================
def test_extract_challenge_problems_empty():
	"""Empty input returns empty list for challenge problems."""
	result = textbook_problems.extract_challenge_problems([])
	assert result == []


#============================================
def test_extract_challenge_problems_no_heading():
	"""No challenge heading returns empty list."""
	lines = ["PROBLEMS", "1.  Only regular problems."]
	result = textbook_problems.extract_challenge_problems(lines)
	assert result == []


#============================================
def test_extract_challenge_stops_at_data_interpretation():
	"""Challenge problems stop at Data Interpretation heading."""
	lines = [
		"Challenge Problems",
		"1.  Challenge one.",
		"Data Interpretation Problems",
		"2.  DI problem.",
	]
	challenge = textbook_problems.extract_challenge_problems(lines)
	assert len(challenge) == 1
	assert challenge[0]["number"] == 1


#============================================
def test_extract_data_interpretation_basic():
	"""Extract data interpretation problems."""
	lines = [
		"Data Interpretation Problems",
		"",
		"5.  Graph reading. Look at the graph.",
		"What does it show?",
		"",
		"Selected Readings for this chapter",
	]
	di = textbook_problems.extract_data_interpretation_problems(lines)
	assert len(di) == 1
	assert di[0]["number"] == 5
	assert "graph" in di[0]["text"].lower()


#============================================
def test_extract_data_interpretation_singular():
	"""Singular Data Interpretation Problem heading works."""
	lines = [
		"Data Interpretation Problem",
		"",
		"10.  Single DI problem. Answer this.",
		"",
	]
	di = textbook_problems.extract_data_interpretation_problems(lines)
	assert len(di) == 1
	assert di[0]["number"] == 10


#============================================
def test_extract_data_interpretation_empty():
	"""Empty input returns empty list for data interpretation."""
	result = textbook_problems.extract_data_interpretation_problems([])
	assert result == []


#============================================
def test_extract_data_interpretation_no_heading():
	"""No DI heading returns empty list."""
	lines = ["PROBLEMS", "1.  Regular."]
	result = textbook_problems.extract_data_interpretation_problems(lines)
	assert result == []


#============================================
def test_full_chapter_all_sections():
	"""Simulate a full chapter with PROBLEMS, Challenge, and DI sections."""
	lines = [
		"Some chapter intro text",
		"PROBLEMS",
		"",
		"1.  What is the structure of glucose?",
		"",
		"2.  Explain the difference between",
		"alpha and beta anomers.",
		"",
		"3.  Draw the Fischer projection.",
		"",
		"Challenge Problems",
		"",
		"4.  Prove that the Gibbs free energy",
		"change for this reaction is negative.",
		"",
		"Data Interpretation Problems",
		"",
		"5.  Examine Figure 12.3 and determine",
		"the Km value for the enzyme.",
		"",
		"Selected Readings for this chapter",
	]
	# regular problems
	problems = textbook_problems.extract_problems(lines)
	assert len(problems) == 3
	assert problems[0]["number"] == 1
	assert problems[2]["number"] == 3

	# challenge problems
	challenge = textbook_problems.extract_challenge_problems(lines)
	assert len(challenge) == 1
	assert challenge[0]["number"] == 4
	assert "Gibbs free energy" in challenge[0]["text"]

	# data interpretation
	di = textbook_problems.extract_data_interpretation_problems(lines)
	assert len(di) == 1
	assert di[0]["number"] == 5
	assert "Km value" in di[0]["text"]


#============================================
def test_problem_text_whitespace_collapsed():
	"""Extra whitespace in problem text is collapsed to single spaces."""
	lines = [
		"PROBLEMS",
		"1.  Text   with   extra    spaces.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert "  " not in problems[0]["text"]


#============================================
def test_problem_number_is_int():
	"""Problem numbers are returned as integers."""
	lines = [
		"PROBLEMS",
		"42.  Problem forty-two.",
	]
	problems = textbook_problems.extract_problems(lines)
	assert isinstance(problems[0]["number"], int)
	assert problems[0]["number"] == 42


#============================================
def test_is_section_terminator_problems_heading():
	"""PROBLEMS heading is recognized as a section terminator."""
	result = textbook_problems._is_section_terminator("PROBLEMS")
	assert result is True


#============================================
def test_is_section_terminator_non_heading():
	"""Regular text is not a section terminator."""
	result = textbook_problems._is_section_terminator("Just regular text")
	assert result is False


#============================================
def test_find_heading_index_found():
	"""_find_heading_index returns correct index when heading exists."""
	lines = ["intro", "PROBLEMS", "1.  Stuff."]
	idx = textbook_problems._find_heading_index(lines, ["PROBLEMS"])
	assert idx == 1


#============================================
def test_find_heading_index_not_found():
	"""_find_heading_index returns -1 when heading is missing."""
	lines = ["intro", "no heading here"]
	idx = textbook_problems._find_heading_index(lines, ["PROBLEMS"])
	assert idx == -1
