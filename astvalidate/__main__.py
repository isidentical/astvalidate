import ast
import tokenize
from argparse import ArgumentParser
from pathlib import Path

from astvalidate import validate


def browse(paths):
    for path in paths:
        if path.is_file():
            yield path
        else:
            yield from path.glob("**/*.py")


def validate_single(path, level):
    with tokenize.open(path) as f:
        source = f.read()
    tree = ast.parse(source)
    return validate(tree, level=level)


def main():
    parser = ArgumentParser(
        description="Validate the integrity of python files"
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("-l", "--level", type=int, default=None)

    options = parser.parse_args()
    for path in browse(options.paths):
        validate_single(path, options.level)
    else:
        print("No problems found!")


if __name__ == "__main__":
    main()
