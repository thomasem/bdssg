import unittest

from generate import (
    extract_title
)

class TestExtractTitle(unittest.TestCase):
    def test_extract_title_hello(self):
        title = extract_title("# Hello")
        expected = "Hello"
        self.assertEqual(title, expected)

    def test_extract_title_complex(self):
        markdown = """

We've got a small note at the top, but the first h1 is below

# Title!
"""
        expected = "Title!"
        self.assertEqual(extract_title(markdown), expected)

    def test_extract_title_raises(self):
        with self.assertRaises(ValueError):
            extract_title("none to be found")
