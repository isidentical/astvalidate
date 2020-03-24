import ast

import pytest

from astvalidate.validators.contextual import ContextualASTValidator


@pytest.mark.parametrize(
    "node, message",
    [
        (ast.Return(), "inside of a function"),
        (
            ast.AsyncFunctionDef(body=[ast.Yield(), ast.Return(1)]),
            "can't be part of async gen",
        ),
        (ast.Continue(), "inside of a loop"),
        (ast.Break(), "inside of a loop"),
        (ast.AsyncFor(), "inside of a coroutine"),
        (
            ast.Try(handlers=[ast.ExceptHandler(), ast.ExceptHandler(type=1)]),
            "must be placed last",
        ),
        (
            ast.Module([1, 2, ast.ImportFrom("__future__")]),
            "must occur at the top",
        ),
    ],
)
def test_simple_ast_validator(node, message):
    validator = ContextualASTValidator()
    with pytest.raises(SyntaxError) as cm:
        validator.validate(ast.fix_missing_locations(node))
    assert cm.match(message)
