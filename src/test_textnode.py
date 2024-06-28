from enum import Enum
from re import split
import unittest

from textnode import TextNode, TextType, split_nodes_delimiter
from htmlnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_init(self):
        node = TextNode("foo", TextType.Bold, "https://url.of.textnode/")
        self.assertEqual(node.text, "foo")
        self.assertEqual(node.text_type, TextType.Bold)
        self.assertEqual(node.url, "https://url.of.textnode/")

    def test_init_url_none(self):
        node = TextNode("foo", TextType.Italic)
        self.assertIsNone(node.url, None)
        
    def test_eq(self):
        node = TextNode("This is a text node", TextType.Bold)
        node2 = TextNode("This is a text node", TextType.Bold)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("foo", TextType.Bold, "https://foo.bar/")
        node2 = TextNode("foo", TextType.Bold, "https://foo.bar/")
        self.assertEqual(node, node2)

    def test_eq_negative_url(self):
        node = TextNode("This is a text node", TextType.Bold,
                        "https://foo.bar/")
        node2 = TextNode("This is a text node", TextType.Bold)
        self.assertNotEqual(node, node2)

    def test_eq_negative_type(self):
        node = TextNode("foo", TextType.Bold)
        node2 = TextNode("foo", TextType.Italic)
        self.assertNotEqual(node, node2)

    def test_repr(self):
        self.assertEqual(str(TextNode("foo bar baz", TextType.Bold)),
            "TextNode(foo bar baz, bold, None)")
        self.assertEqual(
            str(TextNode("foo", TextType.Italic, "https://i.am.url/")),
            "TextNode(foo, italic, https://i.am.url/)"
        )

    def test_to_html_node(self):
        tests = [
            (TextNode("foo", TextType.Text), LeafNode(None, "foo")),
            (TextNode("foo", TextType.Bold), LeafNode('b', "foo")),
            (TextNode("foo", TextType.Italic), LeafNode('i', "foo")),
            (TextNode("foo", TextType.Code), LeafNode('code', "foo")),
            (TextNode("foo", TextType.Link, "https://url.me/"),
             LeafNode('a', "foo", {"href": "https://url.me/"})),
            (TextNode("foo", TextType.Image, "https://img.url/"),
             LeafNode('img', "", {"src": "https://img.url/", "alt": "foo"})),
        ]

        for text_node, expected in tests:
            result = text_node.to_html_node()
            self.assertEqual(expected, result)

    def test_to_html_node_invalid(self):
        class mockTextType(Enum):
            Invalid = "invalid"

        node = TextNode("foo", mockTextType.Invalid) # type: ignore
        with self.assertRaises(ValueError):
            node.to_html_node()


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

if __name__ == "__main__":
    unittest.main()
