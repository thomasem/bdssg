import textnode


def main():
    text = ("This is **text** with an *italic* word and a `code block` and an "
    "![image](https://image.hahaha) and a [link](https://link.url)")
    for node in textnode.text_to_textnodes(text):
        print(node)


if __name__ == "__main__":
    main()
