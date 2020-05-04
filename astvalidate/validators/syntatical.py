import ast

from astvalidate.validators.base import ASTValidator, name_of

LEVEL = 1


class SyntaticalASTValidator(ASTValidator):
    def visit_Assert(self, node):
        if isinstance(node.test, ast.Tuple) and len(node.test.elts) > 0:
            self.warn(
                "Assertion is always true, perhaps remove parentheses?", node,
            )

    def visit_Call(self, node):
        if isinstance(
            node.func,
            (
                ast.Constant,
                ast.Tuple,
                ast.List,
                ast.ListComp,
                ast.Dict,
                ast.DictComp,
                ast.Set,
                ast.SetComp,
                ast.GeneratorExp,
                ast.JoinedStr,
                ast.FormattedValue,
            ),
        ):
            self.warn(
                f"{name_of(node.func)} object is not callable;"
                f"perhaps you missed a comma?",
                node,
            )

    def visit_Subscript(self, node):
        if isinstance(
            node.value, (ast.Set, ast.SetComp, ast.GeneratorExp, ast.Lambda)
        ):
            self.warn(
                f"{name_of(node.value)} object is not subscriptable;"
                f"perhaps you missed a comma?",
                node,
            )
        if isinstance(
            node.value,
            (
                ast.Tuple,
                ast.List,
                ast.ListComp,
                ast.JoinedStr,
                ast.FormattedValue,
            ),
        ):
            if isinstance(node.slice, ast.Constant) and not isinstance(
                node.slice.value, int
            ):
                self.warn(
                    f"{name_of(node.value)} indices must be integers or slices, "
                    f"not {name_of(node.slice)} perhaps you missed a comma?",
                    node,
                )
