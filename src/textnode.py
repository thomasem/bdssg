from typing import Any
from enum import Enum


class TextType(Enum):
    Normal = "normal"
    Bold = "bold"
    Italic = "italic"
    Code = "code"
    Link = "link"
    Image = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None):
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

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
