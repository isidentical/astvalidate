import ast
from pathlib import Path

import pytest

import astvalidate

VALID_FILES = Path(astvalidate.__path__[0])


@pytest.mark.parametrize("file", VALID_FILES.glob("**/*.py"))
def test_all_files_validated(file):
    source = file.read_text()
    astvalidate.validate(ast.parse(source))
