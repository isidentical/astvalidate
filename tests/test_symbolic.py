import ast
import textwrap

import pytest

from astvalidate.validators.symbolic import SymbolicASTValidator


@pytest.mark.parametrize(
    "source, message",
    [
        (
            """
            def x():
                global x
                nonlocal x
            """,
            "can't be both nonlocal and global",
        ),
        (
            """
            nonlocal x
            """,
            "can't be declared as nonlocal",
        ),
        (
            """
            def x(a, *a):
                pass
            """,
            "'a' is duplicated",
        ),
    ],
)
def test_simple_ast_validator(source, message):
    validator = SymbolicASTValidator()
    with pytest.raises(SyntaxError) as cm:
        validator.validate(ast.parse(textwrap.dedent(source)))
    assert cm.match(message)
