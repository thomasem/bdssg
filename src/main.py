import shutil
import os


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
    public_path = os.path.abspath("public")
    static_path = os.path.abspath("static")
    print(f"Copying static files to {public_path}...")
    copy(static_path, public_path)


if __name__ == "__main__":
    main()
