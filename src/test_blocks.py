import unittest

from blocks import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
)
import textnode as tn


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
