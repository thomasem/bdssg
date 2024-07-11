import os

import blocks


def extract_title(markdown: str) -> str:
    title_line = ""
    for line in markdown.strip().splitlines():
        if line.startswith("# "):
            title_line = line
            break

    if not title_line:
        raise ValueError("could not find title")

    return title_line.lstrip("#").strip()


def generate_page(from_path: str, dest_path: str, template_path: str):
    print(f"Generating page from {from_path} to {dest_path}"
          f" using {template_path}")

    source = ""
    with open(from_path) as f:
        source = f.read()

    template = ""
    with open(template_path) as f:
        template = f.read()

    title = extract_title(source)
    source_node = blocks.markdown_to_html_node(source)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", source_node.to_html())

    with open(dest_path, 'w') as f:
        f.write(template)
