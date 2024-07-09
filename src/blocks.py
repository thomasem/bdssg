import abc
import enum
import re


class BlockType(enum.Enum):
    Paragraph = "paragraph"
    Heading = "heading"
    Code = "code"
    Quote = "quote"
    UnorderedList = "unordered_list"
    OrderedList = "ordered_list"


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
