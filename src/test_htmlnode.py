import unittest

from htmlnode import (
    HTMLNode,
    LeafNode,
    ParentNode,
)


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

    def test_eq_positive(self):
        tests = [
            (HTMLNode(), HTMLNode()),
            (HTMLNode('p', "", [], {}), HTMLNode('p', "", [], {})),
            (HTMLNode('b', None), HTMLNode('b', None)),
            (HTMLNode('a', props={"href": "https://u.r.l/"}),
             HTMLNode('a', props={"href": "https://u.r.l/"})),
            (HTMLNode('div', None, [HTMLNode('p', "foo")]),
             HTMLNode('div', None, [HTMLNode('p', "foo")])),
        ]
        for first, second in tests:
            self.assertEqual(first, second)

    def test_eq_negative(self):
        tests = [
            (HTMLNode(), HTMLNode('b')),
            (HTMLNode('p', "", [], {}), HTMLNode('b', "", [], {})),
            (HTMLNode('b', None), HTMLNode('i', None)),
            (HTMLNode('a', props={"href": "https://u.r.l/", "class": "c1"}),
             HTMLNode('a', props={"href": "https://u.r.l/"})),
            (HTMLNode('div', None, [HTMLNode('p', "foo")]),
             HTMLNode('div', None, [HTMLNode('b', "foo")])),
        ]
        for first, second in tests:
            self.assertNotEqual(first, second)


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
        for tag in (None, ''):
            parent = ParentNode(tag, [LeafNode('p', "foo")]) # type: ignore
            with self.assertRaises(ValueError) as error:
                parent.to_html()
            self.assertEqual(str(error.exception),
                             ParentNode.tag_required_error)

    def test_to_html_no_children(self):
        for children in (None, []):
            parent = ParentNode('p', children) # type: ignore
            with self.assertRaises(ValueError) as error:
                parent.to_html()
            self.assertEqual(str(error.exception),
                             ParentNode.children_required_error)

    def test_to_html(self):
        tests = [
            (('p', [LeafNode('b', 'foo')]), "<p><b>foo</b></p>"),
            (('p', [
                LeafNode('b', 'Bold text'),
                LeafNode(None, 'Normal text'),
                LeafNode('i', 'italic text'),
                LeafNode(None, 'Normal text'),
            ]),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"),
            (('div', [
                LeafNode('h1', 'heading'),
                ParentNode('p', [
                    LeafNode('p', 'paragraph right here!'),
                    ParentNode('p', [
                        LeafNode('a', 'linkylink', {'href': "https://u.r.l/"}),
                    ]),
                ], {'class': 'myParagraph'}),
            ], {'class': 'myDiv'}),
            '<div class="myDiv"><h1>heading</h1><p class="myParagraph"><p>paragraph right here!</p><p><a href="https://u.r.l/">linkylink</a></p></p></div>'
            ),
        ]
        for args, expected in tests:
            parent = ParentNode(*args)
            self.assertEqual(expected, parent.to_html())
