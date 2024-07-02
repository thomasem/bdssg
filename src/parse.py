import re

from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType
) -> list[TextNode]:
    """Splits the provided nodes based on a passed in delimiter. It's
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


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    re_mask = r"!\[(.*?)\]\((.*?)\)"
    return re.findall(re_mask, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    re_mask = r"(?<!!)\[(.*?)\]\((.*?)\)"
    return re.findall(re_mask, text)
