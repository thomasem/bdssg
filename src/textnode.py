from typing import Any
from enum import Enum

from htmlnode import HTMLNode, LeafNode


class TextType(Enum):
    Text = "text"
    Bold = "bold"
    Italic = "italic"
    Code = "code"
    Link = "link"
    Image = "image"


class TextNode:
    def __init__(
        self,
        text: str,
        text_type: TextType = TextType.Text,
        url: str | None = None
    ):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TextNode):
            return NotImplemented
        return all([
            self.text == other.text,
            self.text_type == other.text_type,
            self.url == other.url,
        ])

    def to_html_node(self) -> HTMLNode:
        match self.text_type:
            case TextType.Text:
                return LeafNode(None, self.text)
            case TextType.Bold:
                return LeafNode('b', self.text)
            case TextType.Italic:
                return LeafNode('i', self.text)
            case TextType.Code:
                return LeafNode('code', self.text)
            case TextType.Link:
                props = {"href": self.url or ""}
                return LeafNode('a', self.text, props)
            case TextType.Image:
                props = {"src": self.url or "", "alt": self.text}
                return LeafNode('img', "", props)
        raise ValueError(f"invalid text_type {self.text_type.value}")

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType
) -> list[TextNode]:
    """ Splits the provided nodes based on a passed in delimiter. It's
    important to consider false positives, such as when trying to split on `*`
    when the caller will also be splitting on `**`, you should start by
    splitting on `**`, then proceed to `*`.`
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