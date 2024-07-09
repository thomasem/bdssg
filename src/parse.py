from abc import ABC, abstractmethod
from enum import Enum
import re

from textnode import TextNode, TextType
from htmlnode import HTMLNode, ParentNode


class BlockType(Enum):
    Paragraph = "paragraph"
    Heading = "heading"
    Code = "code"
    Quote = "quote"
    UnorderedList = "unordered_list"
    OrderedList = "ordered_list"


class Extractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> list[tuple[str, str]]:
        pass

    @staticmethod
    @abstractmethod
    def string_from_extract(extract: tuple[str, str]) -> str:
        pass

    @staticmethod
    @abstractmethod
    def text_type() -> TextType:
        pass


class ImageExtractor(Extractor):
    re_mask = r"!\[(.*?)\]\((.*?)\)"

    def extract(self, text: str) -> list[tuple[str, str]]:
        return re.findall(self.re_mask, text)

    @staticmethod
    def string_from_extract(extract: tuple[str, str]) -> str:
        return f"![{extract[0]}]({extract[1]})"

    @staticmethod
    def text_type() -> TextType:
        return TextType.Image


class LinkExtractor(Extractor):
    re_mask = r"(?<!!)\[(.*?)\]\((.*?)\)"

    def extract(self, text: str) -> list[tuple[str, str]]:
        return re.findall(self.re_mask, text)

    @staticmethod
    def string_from_extract(extract: tuple[str, str]) -> str:
        return f"[{extract[0]}]({extract[1]})"

    @staticmethod
    def text_type() -> TextType:
        return TextType.Link


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType
) -> list[TextNode]:
    """Splits the provided nodes based on a passed in delimiter. It's
    important to consider false positives, such as when trying to split on `*`
    when the caller will also be splitting on `**`, you should start by
    splitting on `**`, then proceed to `*`.
    """
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.Text:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError('unclosed formatting syntax found')

        for i in range(len(parts)):
            if parts[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(parts[i], TextType.Text))
            else:
                new_nodes.append(TextNode(parts[i], text_type))
    return new_nodes


def split_nodes_extractor(
    old_nodes: list[TextNode],
    extractor: Extractor,
) -> list[TextNode]:
    """Splits the provided nodes based on what's found by a passed in extractor
    """
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.Text:
            new_nodes.append(node)
            continue

        extracts = extractor.extract(node.text)
        if not extracts:
            new_nodes.append(node)
            continue

        leftover = node.text
        for extract in extracts:
            split_str = extractor.string_from_extract(extract)
            new_node = TextNode(extract[0], extractor.text_type(), extract[1])
            # ensure only one split, in case of duplicates which we'll get to
            # in subsequent iterations
            parts = leftover.split(split_str, 1)
            if parts[0] == "":
                new_nodes.append(new_node)
            else:
                new_nodes.extend([TextNode(parts[0], TextType.Text), new_node])

            leftover = parts[1]

        if leftover:
            new_nodes.append(TextNode(leftover, TextType.Text))

    return new_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    """This is done in a specific order to avoid false-positives"""
    new_nodes = [TextNode(text)]
    for extractor in (ImageExtractor(), LinkExtractor()):
        new_nodes = split_nodes_extractor(new_nodes, extractor)

    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.Bold)
    new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.Italic)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.Code)

    return new_nodes


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []
    # Not critical, but trying to be kind to other OS' representation of
    # newlines :)
    for part in re.split(r'(?:\r?\n){2}', markdown):
        if part != "":
            blocks.append(part.strip())
    return blocks


def block_to_block_type(text: str) -> BlockType:
    """This function will determine the type of markdown block that's passed
    in, returning a BlockType. We can assume leading / trailing whitespace is
    already removed from the markdown_to_blocks() call. Hope I don't regret the
    regex. :)
    """
    # If it starts with 1-6 of the "#" character, we have a heading
    if re.match(r'^#{1,6}\ ', text):
        return BlockType.Heading
    # If it starts and ends with three backtick (`) characters, we have a code
    # block
    if text.startswith("```") and text.endswith("```"):
        return BlockType.Code

    lines = text.splitlines()
    flags = re.MULTILINE

    # If all lines start with >, we've got a quote
    if len(re.findall(r'^>.+$', text, flags=flags)) == len(lines):
        return BlockType.Quote

    # If all lines start with * or - and a space, we've got an unordered list
    if len(re.findall(r'^[\*\-]\ .+$', text, flags=flags)) == len(lines):
        return BlockType.UnorderedList

    # If all lines start with "N." and a space, like "1. " or "2. "
    # we have an ordered list as long as the first number is "1"
    if text.startswith("1. ") and \
            len(re.findall(r'^\d+\.\ .+$', text, flags=flags)) == len(lines):
        return BlockType.OrderedList

    return BlockType.Paragraph
