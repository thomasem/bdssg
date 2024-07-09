import abc
import enum
import re

import htmlnode as hn
import textnode as tn


class Block(abc.ABC):
    def __init__(self, text: str):
        self.text = text

    @staticmethod
    @abc.abstractmethod
    def matches(text: str) -> bool:
        pass

    @abc.abstractmethod
    def to_html_node(self) -> hn.HTMLNode:
        pass


class Paragraph(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # Any text can be a paragraph, if we really want it!
        return True

    def to_html_node(self) -> hn.HTMLNode:
        children = []
        nodes = tn.text_to_textnodes(self.text)
        for node in nodes:
            children.append(node.to_html_node())
        return hn.ParentNode('p', children=children)


class Heading(Block):
    @staticmethod
    def matches(text: str) -> bool:
        return re.match(r'^#{1,6}\ ', text) is not None

    def to_html_node(self) -> hn.HTMLNode:
        level = 1
        match = re.match('^#+', self.text)
        if match:
            level = match.span()[1]
        children = []
        for node in tn.text_to_textnodes(self.text):
            children.append(node.to_html_node())
        return hn.ParentNode(f'h{level}', children=children)


class Code(Block):
    @staticmethod
    def matches(text: str) -> bool:
        backticks = '```'
        return text.startswith(backticks) and text.endswith(backticks)

    def to_html_node(self) -> hn.HTMLNode:
        code = hn.LeafNode('code', self.text)
        return hn.ParentNode('pre', children=[code])


class Quote(Block):
    @staticmethod
    def matches(text: str) -> bool:
        lines = text.splitlines()
        if len(lines) < 1:
            return False
        for line in lines:
            if not line.startswith('>'):
                return False
        return True

    def to_html_node(self) -> hn.HTMLNode:
        return hn.LeafNode('blockquote', self.text)


class UnorderedList(Block):
    @staticmethod
    def matches(text: str) -> bool:
        lines = text.splitlines()
        if len(lines) < 1:
            return False
        for line in lines:
            if not (line.startswith('* ') or line.startswith('- ')):
                return False
        return True

    def to_html_node(self) -> hn.HTMLNode:
        children = []
        for node in tn.text_to_textnodes(self.text):
            children.append(
                hn.ParentNode('li', children=[node.to_html_node()]))
        return hn.ParentNode('ul', children=children)


class OrderedList(Block):
    @staticmethod
    def matches(text: str) -> bool:
        lines = text.splitlines()
        if len(lines) < 1 or not lines[0].startswith('1. '):
            return False
        startswith_re = re.compile(r'^\d+\. ')
        for line in lines:
            if not startswith_re.match(line):
                return False
        return True

    def to_html_node(self) -> hn.HTMLNode:
        children = []
        for node in tn.text_to_textnodes(self.text):
            children.append(hn.ParentNode('li', children=[node.to_html_node()]))
        return hn.ParentNode('ol', children=children)


def markdown_to_block_strings(markdown: str) -> list[str]:
    blocks = []
    # Not critical, but trying to be kind to other OS' representation of
    # newlines :)
    for part in re.split(r'(?:\r?\n){2}', markdown):
        if part != "":
            blocks.append(part.strip())
    return blocks


def block_to_block_type(text: str) -> Block:
    """This function will discover the type of markdown block that's passed
    in, returning the appropriate Block object for later use. We can assume
    leading / trailing whitespace is already removed from the
    markdown_to_blocks() call.
    """
    for block_type in (Heading, Code, Quote, UnorderedList, OrderedList):
        if block_type.matches(text):
            return block_type(text)
    return Paragraph(text)
