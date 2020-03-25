import ast
from pathlib import Path

import pytest

import astvalidate

VALID_FILES = Path(astvalidate.__path__[0])
STDLIB_DIR = Path(ast.__file__).parent


@pytest.mark.parametrize("file", VALID_FILES.glob("**/*.py"))
def test_sources(file):
    source = file.read_text()
    astvalidate.validate(ast.parse(source))


@pytest.mark.slow
@pytest.mark.parametrize("file", STDLIB_DIR.glob("*.py"))
def test_all_stdlib(file):
    source = file.read_text()
    astvalidate.validate(ast.parse(source))
