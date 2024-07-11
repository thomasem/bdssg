import shutil
import os

import generate

def copy(src: str, dest: str):
    if os.path.exists(dest):
        print(f"Found content at {dest}, removing...")
        shutil.rmtree(dest)

    print(f"Creating directory {dest}...")
    os.mkdir(dest)

    for basename in os.listdir(src):
        path = os.path.join(src, basename)
        if os.path.isdir(path):
            next_dest = os.path.join(dest, basename)
            print(f"Found directory {path}, copying into {next_dest}")
            copy(path, next_dest)
        else:
            print(f"Copying {path} to {dest}")
            shutil.copy(path, dest)


def main():
    current_path = os.path.abspath(".")
    public_path = os.path.abspath("public")
    static_path = os.path.abspath("static")
    content_path = os.path.abspath("content")

    copy(static_path, public_path)

    index_md_path = os.path.join(content_path, "index.md")
    index_html_path = os.path.join(public_path, "index.html")
    template_path = os.path.join(current_path, "template.html")
    generate.generate_page(index_md_path, index_html_path, template_path)


if __name__ == "__main__":
    main()
