import re

from textnode import TextNode, TextType


# TODO: Consider Extract classes that encapsulates the logic for converting
# to a TextNode, which would help handle cases where the extract doesn't
# two strings, like the tuple[str, str] from extracting an image or a link


class Extractor:
    def extract(self, text: str) -> list[tuple[str, str]]:
        raise NotImplementedError

    def string_from_extract(self, extract: tuple[str, str]) -> str:
        # NOTE: This is a perfect candidate for Extract classes that format
        # themselves for further use
        raise NotImplementedError

    def text_type(self) -> TextType:
        raise NotImplementedError


class ImageExtractor(Extractor):
    re_mask = r"!\[(.*?)\]\((.*?)\)"

    def extract(self, text: str) -> list[tuple[str, str]]:
        return re.findall(self.re_mask, text)

    def string_from_extract(self, extract: tuple[str, str]) -> str:
        return f"![{extract[0]}]({extract[1]})"

    def text_type(self) -> TextType:
        return TextType.Image


class LinkExtractor(Extractor):
    re_mask = r"(?<!!)\[(.*?)\]\((.*?)\)"

    def extract(self, text: str) -> list[tuple[str, str]]:
        return re.findall(self.re_mask, text)

    def string_from_extract(self, extract: tuple[str, str]) -> str:
        return f"[{extract[0]}]({extract[1]})"

    def text_type(self) -> TextType:
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
