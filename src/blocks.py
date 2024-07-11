import abc
import enum
import re

import htmlnode as hn
import textnode as tn


BACKTICKS = "```"


class Block(abc.ABC):
    def __init__(self, text: str, strict: bool = True):
        if strict and not self.matches(text):
            err = f"unexpected value for {type(self).__name__} block"
            raise ValueError(err)
        self.raw = text

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
        return hn.ParentNode('p', children=text_to_children(self.raw.strip()))


class Heading(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # starts with 1-6 '#' characters, followed by a space
        return re.match(r'^#{1,6}\ ', text) is not None

    def to_html_node(self) -> hn.HTMLNode:
        # not likely we'd get this far without it at least being an h1
        level = 1
        # calculate level by finding when the '# character stops showing up
        for i in range(len(self.raw)):
            if self.raw[i] != '#':
                break
            level = i + 1
        children = text_to_children(self.raw[level:].strip())
        return hn.ParentNode(f'h{level}', children=children)


class Code(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # starts and ends with backticks
        return text.startswith(BACKTICKS) and text.endswith(BACKTICKS)

    def to_html_node(self) -> hn.HTMLNode:
        trim = len(BACKTICKS)
        # trim backticks on either side and remove any whitespace to get
        # a clean block, and we aren't parsing any further because it should
        # be pre-formatted, hence the <pre> tag
        code = hn.LeafNode('code', self.raw[trim:-trim].strip())
        return hn.ParentNode('pre', children=[code])


class Quote(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # all lines must start with '>' character
        lines = text.splitlines()
        if len(lines) < 1:
            return False
        for line in lines:
            if not line.startswith('>'):
                return False
        return True

    def to_html_node(self) -> hn.HTMLNode:
        children = []
        stripped_lines = []
        for line in self.raw.splitlines():
            stripped_lines.append(line[1:].strip())
        content = " ".join(stripped_lines)
        return hn.ParentNode('blockquote', children=text_to_children(content))


class UnorderedList(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # all lines must start with a '*' or '-' and a space
        lines = text.splitlines()
        if len(lines) < 1:
            return False
        for line in lines:
            if not (line.startswith('* ') or line.startswith('- ')):
                return False
        return True

    def to_html_node(self) -> hn.HTMLNode:
        children = []
        for line in self.raw.splitlines():
            # trim '*' or '-' and extra space
            children.extend(text_to_children(line[1:].strip(), 'li'))
        return hn.ParentNode('ul', children=children)


class OrderedList(Block):
    @staticmethod
    def matches(text: str) -> bool:
        # first line must start with '1. ' and all lines after must be a
        # number with a period and a space
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
        for line in self.raw.splitlines():
            trim = 0
            for i in range(len(line)):
                if line[i] == '.':
                    trim = i + 1
                    break
            # trim everything up to the first period and extra space
            children.extend(text_to_children(line[trim:].strip(), 'li'))
        return hn.ParentNode('ol', children=children)


def text_to_children(text: str, tag: str | None = None) -> list[hn.HTMLNode]:
    """Convert text to TextNodes and then child HTMLNodes
    """
    children = []
    for node in tn.text_to_textnodes(text):
        children.append(node.to_html_node())
    if tag:
        return [hn.ParentNode(tag, children=children)]
    return children


def block_to_block_type(text: str) -> Block:
    """Find appropriate Block class and initialize for each block
    """
    for block_type in (Heading, Code, Quote, UnorderedList, OrderedList):
        if block_type.matches(text):
            # we can skip the constructor check since we already checked
            return block_type(text, strict=False)
    return Paragraph(text)


def markdown_to_block_strings(markdown: str) -> list[str]:
    """Split full markdown document into block strings to be evaluated later
    """
    # Not critical, but trying to be kind to other OS' representation of
    # newlines. This method is also fairly naive and disallows things like
    # extra newlines in codeblocks as it would split up the block erroneously
    parts = re.split(r'(?:\r?\n){2}', markdown)
    blocks = []
    for i in range(len(parts)):
        if parts[i] == "":
            continue
        blocks.append(parts[i].strip())
    return blocks


def markdown_to_html_node(markdown: str) -> hn.HTMLNode:
    """Take full markdown document and make necessary calls to assemble an
    HTMLNode tree, then return the Parent div that wraps all of it
    """
    block_strings = markdown_to_block_strings(markdown)
    children = []
    for block_string in block_strings:
        children.append(block_to_block_type(block_string).to_html_node())
    return hn.ParentNode('div', children=children)
