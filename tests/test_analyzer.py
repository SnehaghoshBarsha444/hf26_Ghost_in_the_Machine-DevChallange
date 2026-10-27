import unittest

from deadcode.analyzer import analyze_source, detect_language
from deadcode.history import get_history


COBOL_SAMPLE = """IDENTIFICATION DIVISION.
PROGRAM-ID. TEST-PROGRAM.
PROCEDURE DIVISION.
DISPLAY "HELLO".
STOP RUN.
"""
BASIC_SAMPLE = """10 PRINT "HELLO"
20 INPUT A$
30 GOTO 10
"""


class AnalyzerTests(unittest.TestCase):
    def test_detect_cobol_by_extension(self):
        self.assertEqual(detect_language("hello", "sample.cob"), "COBOL")

    def test_detect_basic_by_source(self):
        self.assertEqual(detect_language(BASIC_SAMPLE), "BASIC")

    def test_cobol_structure_and_display(self):
        result = analyze_source(COBOL_SAMPLE, "test.cob")
        titles = [f.title for f in result.findings]
        self.assertIn("COBOL structure", titles)
        self.assertIn("Output statement", titles)
        self.assertEqual(result.language, "COBOL")

    def test_basic_jump_is_flagged(self):
        result = analyze_source(BASIC_SAMPLE, "test.bas")
        self.assertTrue(any(f.title == "Line-number jump" for f in result.findings))
        self.assertTrue(any(f.title == "Interactive input" for f in result.findings))

    def test_empty_source(self):
        result = analyze_source("   ", "empty.bas")
        self.assertTrue(any(f.title == "Empty source" for f in result.findings))

    def test_history_alias(self):
        self.assertEqual(get_history("cob").get("name"), "COBOL")

    def test_unknown_history_rejected(self):
        with self.assertRaises(ValueError):
            get_history("fortran")


if __name__ == "__main__":
    unittest.main()
