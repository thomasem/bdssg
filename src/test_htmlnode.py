import unittest

from htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_init_none(self):
        empty = HTMLNode()
        self.assertIsNone(empty.tag)
        self.assertIsNone(empty.value)
        self.assertIsNone(empty.children)
        self.assertIsNone(empty.props)

    def test_props_to_html(self):
        tests = [
            (None, ''),
            ({}, ''),
            ({"target": "_blank", "href": "https://i.am.url/"},
            ' target="_blank" href="https://i.am.url/"'),
        ]
        for props, expected in tests:
            node = HTMLNode(props=props)
            self.assertEqual(expected, node.props_to_html())


class TestLeafNode(unittest.TestCase):
    def test_to_html(self):
        tests = [
            ((None, "I'm simply text!"), "I'm simply text!"),
            (('p', "I'm a paragraph!"), "<p>I'm a paragraph!</p>"),
            (('a', "I'm a link!", {'href': "https://i.am.url/"}),
            "<a href=\"https://i.am.url/\">I'm a link!</a>"),
        ]
        for args, expected in tests:
            leaf = LeafNode(*args)
            self.assertEqual(expected, leaf.to_html())

    def test_init_value_none(self):
        with self.assertRaises(ValueError):
            leaf = LeafNode(tag='p', value=None)