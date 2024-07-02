from enum import Enum
import unittest

from textnode import TextNode, TextType
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


if __name__ == "__main__":
    unittest.main()
