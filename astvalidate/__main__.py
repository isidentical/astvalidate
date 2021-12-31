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
    with tokenize.open(path) as stream:
        tree = ast.parse(stream.read())

    return validate(tree, level=level, fail_fast=False)


def main():
    parser = ArgumentParser(
        description="Validate the integrity of python files"
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("-l", "--level", type=int, default=None)

    options = parser.parse_args()
    for path in browse(options.paths):
        try:
            status = validate_single(path, options.level)
        except Exception as exc:
            print("~", str(path), "(" + str(exc) + ")")

        print("✅" if status else "❌", str(path))


if __name__ == "__main__":
    main()
