import ast
import tokenize
from argparse import ArgumentParser

from astvalidate import IGNORE, validate


def main():
    parser = ArgumentParser(
        description="Validate the integrity of python files"
    )
    parser.add_argument("file")
    parser.add_argument("--level", type=int, default=IGNORE)

    options = parser.parse_args()
    with tokenize.open(options.file) as f:
        source = f.read()
    tree = ast.parse(source)
    if validate(tree, level=options.level):
        print("No problem found on given file!")


if __name__ == "__main__":
    main()
