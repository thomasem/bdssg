import unittest

from blocks import (
    Code,
    Heading,
    OrderedList,
    Paragraph,
    Quote,
    UnorderedList,
    block_to_block_type,
    markdown_to_block_strings,
    markdown_to_html_node,
    text_to_children,
)
import textnode as tn
import htmlnode as hn


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_block_strings(self):
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
        results = markdown_to_block_strings(markdown)
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
        expected_types = [
            UnorderedList,
            Paragraph,
            Quote,
            Code,
            Heading,
            Heading,
            OrderedList,
        ]
        self.assertEqual(len(blocks), len(expected_types))
        for block, expected in zip(blocks, expected_types):
            self.assertIsInstance(block_to_block_type(block), expected)

    def test_block_to_block_type_negative(self):
        blocks = [
            "2. counting not starting at 1\n3. making sandwiches",
            "####### I don't go to 7 levels",
            "def ```main()``` is not a code block, but more inline",
            "> almost a block quote\n but not really",
            "* I was a list\n until I forgot what I was doing",
        ]
        for block in blocks:
            self.assertIsInstance(block_to_block_type(block), Paragraph)


class TestTextToChildren(unittest.TestCase):
    def test_text_to_children_no_tag(self):
        text = "A **bold** word, an *italic* one, and a little `code()`"
        children = text_to_children(text)
        expected = [
            hn.LeafNode(None, "A "),
            hn.LeafNode('b', "bold"),
            hn.LeafNode(None, " word, an "),
            hn.LeafNode('i', "italic"),
            hn.LeafNode(None, " one, and a little "),
            hn.LeafNode('code', "code()"),
        ]
        self.assertEqual(children, expected)

    def test_text_to_children_with_tag(self):
        text = "A **bold** word, an *italic* one, and a little `code()`"
        children = text_to_children(text, 'p')
        expected = [hn.ParentNode('p', children=[
            hn.LeafNode(None, "A "),
            hn.LeafNode('b', "bold"),
            hn.LeafNode(None, " word, an "),
            hn.LeafNode('i', "italic"),
            hn.LeafNode(None, " one, and a little "),
            hn.LeafNode('code', "code()"),
        ])]
        self.assertEqual(children, expected)


class TestBlockTypes(unittest.TestCase):
    def test_strict_block_raises(self):
        with self.assertRaises(ValueError):
            Heading("I used to be a heading, "
                    "but then I took an arrow to the knee")
            Code("Look at all this NOT code...")
            Quote("I'm not actually a quote!")
            UnorderedList("1. convert to an unordered list")
            OrderedList("* convert to an ordered list")

    def test_paragraph_to_html_node(self):
        p = Paragraph("here's a *paragraph* with a [link](https://foo.bar/)")
        node = p.to_html_node()
        expected = hn.ParentNode('p', children=[
            hn.LeafNode(None, "here's a "),
            hn.LeafNode('i', "paragraph"),
            hn.LeafNode(None, " with a "),
            hn.LeafNode('a', "link", {"href": "https://foo.bar/"}),
        ])
        self.assertEqual(node, expected)

    def test_heading_to_html_node(self):
        h3 = Heading("### Heading 3")
        node = h3.to_html_node()
        expected = hn.ParentNode('h3', children=[
            hn.LeafNode(None, "Heading 3"),
        ])
        self.assertEqual(node, expected)

    def test_code_to_html_node(self):
        code = Code("```\ndef hello():\n    print('hello!')\n```")
        node = code.to_html_node()
        expected = hn.ParentNode('pre', children=[
            hn.LeafNode('code', "def hello():\n    print('hello!')"),
        ])
        self.assertEqual(node, expected)

    def test_quote_to_html_node(self):
        text = """
> Failure is success in progress.
> A clever person solves a problem. A wise person avoids it.
"""
        node = Quote(text.strip()).to_html_node()
        expected = hn.ParentNode('blockquote', children=[
            hn.LeafNode(None,
            "Failure is success in progress."
            " A clever person solves a problem."
            " A wise person avoids it."),
        ])
        self.assertEqual(node, expected)

    def test_unordered_list_to_html_node(self):
        text = """
* very little
- muy pequeña
* **big** house
- casa **grande**
"""
        node = UnorderedList(text.strip()).to_html_node()
        expected = hn.ParentNode('ul', children=[
            hn.ParentNode('li', children=[hn.LeafNode(None,"very little")]),
            hn.ParentNode('li', children=[hn.LeafNode(None, "muy pequeña")]),
            hn.ParentNode('li', children=[
                hn.LeafNode('b', "big"),
                hn.LeafNode(None, " house")
            ]),
            hn.ParentNode('li', children=[
                hn.LeafNode(None, "casa "),
                hn.LeafNode('b', "grande")
            ])
        ])
        self.assertEqual(node, expected)

    def test_ordered_list_to_html_node(self):
        text = """
1. very little
2. muy pequeña
3. **big** house
4. casa **grande**
"""
        node = OrderedList(text.strip()).to_html_node()
        expected = hn.ParentNode('ol', children=[
            hn.ParentNode('li', children=[hn.LeafNode(None,"very little")]),
            hn.ParentNode('li', children=[hn.LeafNode(None, "muy pequeña")]),
            hn.ParentNode('li', children=[
                hn.LeafNode('b', "big"),
                hn.LeafNode(None, " house")
            ]),
            hn.ParentNode('li', children=[
                hn.LeafNode(None, "casa "),
                hn.LeafNode('b', "grande")
            ])
        ])
        self.assertEqual(node, expected)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_markdown_to_html_node(self):
        markdown = """
# heading 1

## unordered list below

* unordered list *item 1*
- unordered list **item 2**
* unordered list item 3

A silly paragraph

>a block quote
> with just a little more

```
and now a code block
```

## ordered list below

1. ordered list *item 1*
2. ordered list **item 2**
3. ordered list item 3
"""
        node = markdown_to_html_node(markdown)
        expected = hn.ParentNode('div', children=[
            hn.ParentNode('h1', children=[hn.LeafNode(None, "heading 1")]),
            hn.ParentNode('h2', children=[
                hn.LeafNode(None, "unordered list below")
            ]),
            hn.ParentNode('ul', children=[
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "unordered list "),
                    hn.LeafNode('i', "item 1")
                ]),
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "unordered list "),
                    hn.LeafNode('b', "item 2")
                ]),
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "unordered list item 3")
                ])
            ]),
            hn.ParentNode('p', children=[\
                hn.LeafNode(None, "A silly paragraph")
            ]),
            hn.ParentNode('blockquote', children=[
                hn.LeafNode(None, "a block quote with just a little more")
            ]),
            hn.ParentNode('pre', children=[
                hn.LeafNode('code', "and now a code block")
            ]),
            hn.ParentNode('h2', children=[
                hn.LeafNode(None, "ordered list below")
            ]),
            hn.ParentNode('ol', children=[
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "ordered list "),
                    hn.LeafNode('i', "item 1")
                ]),
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "ordered list "),
                    hn.LeafNode('b', "item 2")
                ]),
                hn.ParentNode('li', children=[
                    hn.LeafNode(None, "ordered list item 3")
                ])
            ])
        ])
        self.assertEqual(node, expected)


if __name__ == "__main__":
    unittest.main()
