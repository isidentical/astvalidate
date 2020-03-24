import ast

import pytest

from astvalidate.simple import SimpleASTValidator


@pytest.mark.parametrize(
    "node",
    [
        ast.FunctionDef(body=[]),
        ast.AsyncFunctionDef(body=[]),
        ast.arguments(
            defaults=[1],
            posonlyargs=[],
            args=[],
            kw_defaults=[],
            kwonlyargs=[],
        ),
        ast.arguments(
            defaults=[],
            posonlyargs=[],
            args=[],
            kw_defaults=[1],
            kwonlyargs=[],
        ),
        ast.AnnAssign(
            simple=True, target=ast.Tuple(ast.Name("a", ast.Load()))
        ),
        ast.With(items=[]),
        ast.Raise(exc=None, cause=1),
        ast.Try(body=[]),
        ast.Try(body=[ast.Pass()], handlers=[], finalbody=[]),
        ast.Try(
            body=[ast.Pass()],
            handlers=[],
            finalbody=[ast.Pass()],
            orelse=[ast.Pass()],
        ),
        ast.ImportFrom(level=-1, names=[1]),
        ast.BoolOp(values=[1]),
        ast.Dict(keys=[1], values=[]),
        ast.Compare(comparators=[]),
        ast.Compare(comparators=[1], ops=[]),
        ast.Constant(value=int),
        ast.Constant(value=(1, 2, int)),
        ast.ListComp(generators=[]),
    ],
)
def test_simple_ast_validator(node):
    validator = SimpleASTValidator()
    with pytest.raises(SyntaxError) as cm:
        validator.validate(ast.fix_missing_locations(node))
    assert cm.value.node is node
    print(cm.value)
