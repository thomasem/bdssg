import unittest

from parse import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter_bold_one(self):
        text = "I **can't** do that, Dave."
        result = split_nodes_delimiter([TextNode(text)], "**", TextType.Bold)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Bold),
            TextNode(" do that, Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_bold_many(self):
        text = "I **can't** do **that**, Dave."
        result = split_nodes_delimiter([TextNode(text)], "**", TextType.Bold)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Bold),
            TextNode(" do ", TextType.Text),
            TextNode("that", TextType.Bold),
            TextNode(", Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)
    
    def test_split_nodes_delimiter_bold_starts_and_ends(self):
        text = "**I can't** do *that*, **Dave.**"
        result = split_nodes_delimiter([TextNode(text)], "**", TextType.Bold)
        expected = [
            TextNode("I can't", TextType.Bold),
            TextNode(" do *that*, ", TextType.Text),
            TextNode("Dave.", TextType.Bold),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_italic_one(self):
        text = "I *can't* do that, Dave."
        result = split_nodes_delimiter([TextNode(text)], "*", TextType.Italic)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Italic),
            TextNode(" do that, Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_italic_many(self):
        text = "I *can't* do *that*, Dave."
        result = split_nodes_delimiter([TextNode(text)], "*", TextType.Italic)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Italic),
            TextNode(" do ", TextType.Text),
            TextNode("that", TextType.Italic),
            TextNode(", Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_italic_starts_and_ends(self):
        text = "*I can't* do `that`, *Dave.*"
        result = split_nodes_delimiter([TextNode(text)], "*", TextType.Italic)
        expected = [
            TextNode("I can't", TextType.Italic),
            TextNode(" do `that`, ", TextType.Text),
            TextNode("Dave.", TextType.Italic),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_code_one(self):
        text = "I `can't` do that, Dave."
        result = split_nodes_delimiter([TextNode(text)], "`", TextType.Code)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Code),
            TextNode(" do that, Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_code_many(self):
        text = "I `can't` do `that`, Dave."
        result = split_nodes_delimiter([TextNode(text)], "`", TextType.Code)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Code),
            TextNode(" do ", TextType.Text),
            TextNode("that", TextType.Code),
            TextNode(", Dave.", TextType.Text),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_code_starts_and_ends(self):
        text = "`I can't` do *that*, `Dave.`"
        result = split_nodes_delimiter([TextNode(text)], "`", TextType.Code)
        expected = [
            TextNode("I can't", TextType.Code),
            TextNode(" do *that*, ", TextType.Text),
            TextNode("Dave.", TextType.Code),
        ]
        self.assertEqual(expected, result)

    def test_split_nodes_delimiter_code_bold_italic(self):
        # Order matters to avoid false-positives, such as between ** and *
        text = "I **can't** do `that`, *Dave*."
        results = split_nodes_delimiter([TextNode(text)], "`", TextType.Code)
        results = split_nodes_delimiter(results, "**", TextType.Bold)
        results = split_nodes_delimiter(results, "*", TextType.Italic)
        expected = [
            TextNode("I ", TextType.Text),
            TextNode("can't", TextType.Bold),
            TextNode(" do ", TextType.Text),
            TextNode("that", TextType.Code),
            TextNode(", ", TextType.Text),
            TextNode("Dave", TextType.Italic),
            TextNode(".", TextType.Text),
        ]
        self.assertEqual(expected, results)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        tests = [
            ("![at the beginning](foo.com)",
             [("at the beginning", "foo.com")]),
            ("this one is ![in the middle](foo.com) of the text",
             [("in the middle", "foo.com")]),
            ("with this one ![at the end](foo.com)",
             [("at the end", "foo.com")])
        ]
        for text, expected in tests:
            results = extract_markdown_images(text)
            self.assertEqual(expected, results)

    def test_extract_markdown_images_many(self):
        text = ("there is ![one here](http://foo.bar.baz/) and then"
                "![this one](https://i.am.url/) here")
        expected = [
            ("one here", "http://foo.bar.baz/"),
            ("this one", "https://i.am.url/"),
        ]
        result = extract_markdown_images(text)
        self.assertEqual(expected, result)

    def test_extract_markdown_images_negative(self):
        tests = [
            ("this is not! an [image](http://but.a.link) here", []),
            ("this is a [link](foo.baz) and ![image](http://hehe.com)",
             [("image", "http://hehe.com")]),
        ]
        for text, expected in tests:
            result = extract_markdown_images(text)
            self.assertEqual(expected, result)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        tests = [
            ("[at the beginning](foo.com)",
             [("at the beginning", "foo.com")]),
            ("this one is [in the middle](foo.com) of the text",
             [("in the middle", "foo.com")]),
            ("with this one [at the end](foo.com)",
             [("at the end", "foo.com")])
        ]
        for text, expected in tests:
            results = extract_markdown_links(text)
            self.assertEqual(expected, results)

    def test_extract_markdown_images_many(self):
        text = ("there is [one here](http://foo.bar.baz/) and then"
                "[this one](https://i.am.url/) here")
        expected = [
            ("one here", "http://foo.bar.baz/"),
            ("this one", "https://i.am.url/"),
        ]
        result = extract_markdown_links(text)
        self.assertEqual(expected, result)

    def test_extract_markdown_images_negative(self):
        tests = [
            ("this is not a ![link](http://but.an.image) here", []),
            ("this is a [link](foo.baz) and ![image](http://hehe.com)",
             [("link", "foo.baz")]),
        ]
        for text, expected in tests:
            result = extract_markdown_links(text)
            self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
