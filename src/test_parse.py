import unittest

from parse import (
    BlockType,
    ImageExtractor,
    LinkExtractor,
    block_to_block_type,
    markdown_to_blocks,
    split_nodes_delimiter,
    split_nodes_extractor,
    text_to_textnodes,
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

    def test_split_nodes_delimiter_unclosed(self):
        text = "I **can't do that, Dave."
        with self.assertRaises(ValueError) as error:
            split_nodes_delimiter([TextNode(text)], "**", TextType.Bold)


class TestImageExtractor(unittest.TestCase):
    extractor = ImageExtractor()

    def test_extract(self):
        tests = [
            ("![at the beginning](foo.com)",
             [("at the beginning", "foo.com")]),
            ("this one is ![in the middle](foo.com) of the text",
             [("in the middle", "foo.com")]),
            ("with this one ![at the end](foo.com)",
             [("at the end", "foo.com")])
        ]
        for text, expected in tests:
            results = self.extractor.extract(text)
            self.assertEqual(expected, results)

    def test_extract_many(self):
        text = ("there is ![one here](http://foo.bar.baz/) and then"
                "![this one](https://i.am.url/) here")
        expected = [
            ("one here", "http://foo.bar.baz/"),
            ("this one", "https://i.am.url/"),
        ]
        result = self.extractor.extract(text)
        self.assertEqual(expected, result)

    def test_extract_negative(self):
        tests = [
            ("this is not! an [image](http://but.a.link) here", []),
            ("this is a [link](foo.baz) and ![image](http://hehe.com)",
             [("image", "http://hehe.com")]),
        ]
        for text, expected in tests:
            result = self.extractor.extract(text)
            self.assertEqual(expected, result)

    def test_string_from_extract(self):
        extract = ("alt text", "https://i.am.url/")
        expected = "![alt text](https://i.am.url/)"
        result = self.extractor.string_from_extract(extract)
        self.assertEqual(expected, result)


class TestLinkExtractor(unittest.TestCase):
    extractor = LinkExtractor()

    def test_extract(self):
        tests = [
            ("[at the beginning](foo.com)",
             [("at the beginning", "foo.com")]),
            ("this one is [in the middle](foo.com) of the text",
             [("in the middle", "foo.com")]),
            ("with this one [at the end](foo.com)",
             [("at the end", "foo.com")])
        ]
        for text, expected in tests:
            results = self.extractor.extract(text)
            self.assertEqual(expected, results)

    def test_extract_many(self):
        text = ("there is [one here](http://foo.bar.baz/) and then"
                "[this one](https://i.am.url/) here")
        expected = [
            ("one here", "http://foo.bar.baz/"),
            ("this one", "https://i.am.url/"),
        ]
        result = self.extractor.extract(text)
        self.assertEqual(expected, result)

    def test_extract_negative(self):
        tests = [
            ("this is not a ![link](http://but.an.image) here", []),
            ("this is a [link](foo.baz) and ![image](http://hehe.com)",
             [("link", "foo.baz")]),
        ]
        for text, expected in tests:
            result = self.extractor.extract(text)
            self.assertEqual(expected, result)

    def test_string_from_extract(self):
        extract = ("link text", "https://i.am.url/")
        expected = "[link text](https://i.am.url/)"
        result = self.extractor.string_from_extract(extract)
        self.assertEqual(expected, result)


class TestSplitNodesExtractor(unittest.TestCase):
    def test_split_nodes_images(self):
        text = TextNode((
            "This is text with an "
            "![image](https://i.am.url/cat.png)"
            " and another "
            "![second image](https://i.am.url/dog.png)"
            " right here"
        ), TextType.Text)
        expected = [
            TextNode("This is text with an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.am.url/cat.png"),
            TextNode(" and another ", TextType.Text),
            TextNode("second image", TextType.Image,
                     "https://i.am.url/dog.png"),
            TextNode(" right here", TextType.Text),
        ]
        results = split_nodes_extractor([text], ImageExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_one_image(self):
        text = TextNode("![image](https://i.am.url/cat.png)", TextType.Text)
        expected = [
            TextNode("image", TextType.Image, "https://i.am.url/cat.png"),
        ]
        results = split_nodes_extractor([text], ImageExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_image_mixed(self):
        text = TextNode((
            "This is text with an "
            "![image](https://i.am.url/cat.png)"
            " and a [link](https://i.am.url/link) right here"
        ), TextType.Text)
        expected = [
            TextNode("This is text with an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.am.url/cat.png"),
            TextNode(" and a [link](https://i.am.url/link) right here",
                     TextType.Text),
        ]
        results = split_nodes_extractor([text], ImageExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_links(self):
        text = TextNode((
            "This is text with an "
            "[link](https://i.am.url/link)"
            " and another "
            "[second link](https://i.am.url/second)"
            " right here"
        ), TextType.Text)
        expected = [
            TextNode("This is text with an ", TextType.Text),
            TextNode("link", TextType.Link, "https://i.am.url/link"),
            TextNode(" and another ", TextType.Text),
            TextNode("second link", TextType.Link,
                     "https://i.am.url/second"),
            TextNode(" right here", TextType.Text),
        ]
        results = split_nodes_extractor([text], LinkExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_one_link(self):
        text = TextNode("[link](https://i.am.url/link)", TextType.Text)
        expected = [
            TextNode("link", TextType.Link, "https://i.am.url/link"),
        ]
        results = split_nodes_extractor([text], LinkExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_link_mixed(self):
        text = TextNode((
            "This is text with an "
            "![image](https://i.am.url/cat.png)"
            " and a [link](https://i.am.url/link) right here"
        ), TextType.Text)
        expected = [
            TextNode((
                "This is text with an ![image](https://i.am.url/cat.png) "
                "and a "
            ), TextType.Text),
            TextNode("link", TextType.Link, "https://i.am.url/link"),
            TextNode(" right here", TextType.Text),
        ]
        results = split_nodes_extractor([text], LinkExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_link_last(self):
        text = TextNode("lookie [link](https://i.am.url/link)", TextType.Text)
        expected = [
            TextNode("lookie ", TextType.Text),
            TextNode("link", TextType.Link, "https://i.am.url/link"),
        ]
        results = split_nodes_extractor([text], LinkExtractor())
        self.assertEqual(expected, results)

    def test_split_nodes_link_first(self):
        text = TextNode("[link](https://i.am.url/link) look!", TextType.Text)
        expected = [
            TextNode("link", TextType.Link, "https://i.am.url/link"),
            TextNode(" look!", TextType.Text),
        ]
        results = split_nodes_extractor([text], LinkExtractor())
        self.assertEqual(expected, results)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = ("This is **text** with an *italic* word and a `code block` "
        "and an ![image](https://i.am.url/image) and a "
        "[link](https://i.am.url/link)")
        expected = [
            TextNode("This is ", TextType.Text),
            TextNode("text", TextType.Bold),
            TextNode(" with an ", TextType.Text),
            TextNode("italic", TextType.Italic),
            TextNode(" word and a ", TextType.Text),
            TextNode("code block", TextType.Code),
            TextNode(" and an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.am.url/image"),
            TextNode(" and a ", TextType.Text),
            TextNode("link", TextType.Link, "https://i.am.url/link")
        ]
        results = text_to_textnodes(text)
        self.assertEqual(expected, results)

    def test_text_to_textnodes_reverse(self):
        text = ("This is a [link](https://i.am.url/link) and an "
        "![image](https://i.am.url/image) and **text** with an *italic* word "
        "and a `code block`")
        expected = [
            TextNode("This is a ", TextType.Text),
            TextNode("link", TextType.Link, "https://i.am.url/link"),
            TextNode(" and an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.am.url/image"),
            TextNode(" and ", TextType.Text),
            TextNode("text", TextType.Bold),
            TextNode(" with an ", TextType.Text),
            TextNode("italic", TextType.Italic),
            TextNode(" word and a ", TextType.Text),
            TextNode("code block", TextType.Code),
        ]
        results = text_to_textnodes(text)
        self.assertEqual(expected, results)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        expected = [
            "This is **bolded** paragraph",
            ("This is another paragraph with *italic* text and `code` here\n"
             "This is the same paragraph on a new line"),
            "* This is a list\n* with items",
        ]
        results = markdown_to_blocks(markdown)
        self.assertEqual(expected, results)


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type(self):
        blocks = [
            "* foo\n* bar",
            "I'm just a little paragraph\nThere's nothing to see here!",
            ">Ask not what you can do for your country!\n>Ask what's for lunch.",
            "```\ndef main():\n    print('hello, world!')\n```",
            "# Shopping list",
            "###### Essentials",
            "1. apples\n4. beer\n5. beer\n6. soft pretzels\n10. mustard",
        ]
        expected = [
            BlockType.UnorderedList,
            BlockType.Paragraph,
            BlockType.Quote,
            BlockType.Code,
            BlockType.Heading,
            BlockType.Heading,
            BlockType.OrderedList
        ]
        self.assertEqual(len(blocks), len(expected))
        for block, expected in zip(blocks, expected):
            self.assertEqual(expected, block_to_block_type(block))

    def test_block_to_block_type_negative(self):
        blocks = [
            "2. counting not starting at 1\n3. making sandwiches",
            "####### I don't go to 7 levels",
            "def ```main()``` is not a code block, but more inline",
            "> almost a block quote\n but not really",
            "* I was a list\n until I forgot what I was doing",
        ]
        for block in blocks:
            self.assertEqual(BlockType.Paragraph, block_to_block_type(block))


if __name__ == "__main__":
    unittest.main()
