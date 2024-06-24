import unittest

from textnode import TextNode


class TestTextNode(unittest.TestCase):
    def test_init(self):
        node = TextNode("foo", "bold", "https://url.of.textnode/")
        self.assertEqual(node.text, "foo")
        self.assertEqual(node.text_type, "bold")
        self.assertEqual(node.url, "https://url.of.textnode/")

    def test_init_url_none(self):
        node = TextNode("foo", "italic")
        self.assertIsNone(node.url, None)
        
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("foo", "bold", "https://foo.bar/")
        node2 = TextNode("foo", "bold", "https://foo.bar/")
        self.assertEqual(node, node2)

    def test_eq_negative_url(self):
        node = TextNode("This is a text node", "bold", "https://foo.bar/")
        node2 = TextNode("This is a text node", "bold")
        self.assertNotEqual(node, node2)

    def test_eq_negative_type(self):
        node = TextNode("foo", "bold")
        node2 = TextNode("foo", "italic")
        self.assertNotEqual(node, node2)

    def test_repr(self):
        self.assertEqual(str(TextNode("foo bar baz", "bold")),
            "TextNode(foo bar baz, bold, None)")
        self.assertEqual(str(TextNode("foo", "italic", "https://i.am.url/")),
            "TextNode(foo, italic, https://i.am.url/)")


if __name__ == "__main__":
    unittest.main()
