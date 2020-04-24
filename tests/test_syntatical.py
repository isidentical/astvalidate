import ast

import pytest

from astvalidate.validators.syntatical import SyntaticalASTValidator


@pytest.mark.parametrize(
    "source, message",
    [
        ("assert (1,)", "Assertion is always true"),
        ("assert (1, 2, 3)", "Assertion is always true"),
        ("1()", "object is not callable"),
        ("(1, 2)()", "object is not callable"),
        ("{'a':'b'}()", "object is not callable"),
        ("{1,2}[1]", "object is not subscriptable"),
        ("(lambda x:None)[1]", "object is not subscriptable"),
        ("[lol]['a']", "indices must be integers or slices"),
        ("[lol][1.0]", "indices must be integers or slices"),
    ],
)
def test_simple_ast_validator(source, message):
    validator = SyntaticalASTValidator()
    with pytest.warns(SyntaxWarning, match=message) as cm:
        node = ast.parse(source)
        validator.validate(node)
