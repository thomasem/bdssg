from typing import TypeVar


HTMLNodeType = TypeVar('HTMLNodeType', bound='HTMLNode')


class HTMLNode:
    def __init__(self, tag: str | None = None, value: str | None = None,
                 children: list[HTMLNodeType] | None = None,
                 props: dict[str, str] | None = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self) -> str:
        raise NotImplementedError
    
    def props_to_html(self) -> str:
        prop_string = ""
        if self.props is None:
            return prop_string
        for key, value in self.props.items():
            prop_string += f' {key}="{value}"'
        return prop_string
    
    def __repr__(self):
        return (f"HTMLNode("
            f"{self.tag},"
            f"{self.value},"
            f"{self.children},"
            f"{self.props})"
        )


class LeafNode(HTMLNode):
    value_required_error = "value required for LeafNode"

    def __init__ (self, tag: str | None, value: str,
                  props: dict[str, str] | None = None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self) -> str:
        # NOTE / TODO: checking specifically for None here because an empty
        # string seems like it should be OK? Double-check this!
        if self.value is None:
            raise ValueError(self.value_required_error)
        if not self.tag:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    tag_required_error = "tag required for ParentNode"
    children_required_error = "children required for ParentNode"

    def __init__(self, tag: str, children: list[HTMLNodeType],
                 props: dict[str, str] | None = None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError(self.tag_required_error)
        if not self.children:
            raise ValueError(self.children_required_error)

        html = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            html += f"{child.to_html()}"
        return html + f"</{self.tag}>"