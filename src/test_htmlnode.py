import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_empty(self):
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

    def test_to_html_value_none(self):
        leaf = LeafNode('p', None) # type: ignore
        with self.assertRaises(ValueError):
            leaf.to_html()


class TestParentNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        parent = ParentNode(None, [LeafNode('p', "foo")]) # type: ignore
        with self.assertRaises(ValueError) as error:
            parent.to_html()
        self.assertEqual(str(error.exception), ParentNode.tag_required_error)

    def test_to_html_falsy_tag(self):
        parent = ParentNode('', [LeafNode('p', "foo")])
        with self.assertRaises(ValueError) as error:
            parent.to_html()
        self.assertEqual(str(error.exception), ParentNode.tag_required_error)

    def test_to_html_no_children(self):
        parent = ParentNode('p', [])
        with self.assertRaises(ValueError) as error:
            parent.to_html()
        self.assertEqual(str(error.exception),
                         ParentNode.children_required_error)

    def test_to_html(self):
        pass