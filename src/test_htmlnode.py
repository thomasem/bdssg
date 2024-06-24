import unittest

from htmlnode import HTMLNode


class HTMLNodeTest(unittest.TestCase):
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
