from textnode import TextNode, TextType

def main():
    test = TextNode("foo", TextType.Bold, "https://boot.dev")
    print(test)

if __name__ == "__main__":
    main()
