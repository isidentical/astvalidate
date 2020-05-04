import ast

from astvalidate.validators.base import ASTValidator, name_of

CONSTANT_TYPES = frozenset((int, float, complex, bool, str, bytes))
CONSTANT_SEQUENCE_TYPES = frozenset((tuple, frozenset))


class SimpleASTValidator(ASTValidator):
    LEVEL = 1

    def validate_body(self, node):
        if len(node.body) < 1:
            self.invalidate(
                f"{name_of(node)}'s body should hold at least one statement",
                node,
            )

    def validate_names(self, node):
        if len(node.names) < 1:
            self.invalidate(
                f"{name_of(node)}'s names should hold at least one name", node
            )

    def validate_targets(self, node):
        if len(node.targets) < 1:
            self.invalidate(
                f"{name_of(node)}'s targets should hold at least one target",
                node,
            )

    def validate_statement(self, node):
        self.validate_body(node)

    def validate_comprehension(self, node):
        if len(node.generators) < 1:
            self.invalidate(
                f"{name_of(node)} should have at least one generator", node
            )

    def visit_arguments(self, node):
        if len(node.defaults) > len(node.posonlyargs) + len(node.args):
            self.invalidate(
                f"More positional defaults than args on {name_of(node)}'s arguments",
                node,
            )

        if len(node.kw_defaults) != len(node.kwonlyargs):
            self.invalidate(
                f"Length of kwonlyargs is not the same as kw_defaults on {name_of(node)}'s arguments",
                node,
            )

    def visit_AnnAssign(self, node):
        if node.simple and not isinstance(node.target, ast.Name):
            self.invalidate(
                f"Simple {name_of(node)} was expecting a Name node but found {name_of(node.target)}",
                node,
            )

    def visit_With(self, node):
        if len(node.items) < 1:
            self.invalidate(
                f"{name_of(node)}'s items should hold at least one item", node
            )

    def visit_Raise(self, node):
        if node.exc is None and node.cause is not None:
            self.invalidate(
                f"{name_of(node)}'s cause can't be used without setting an exception",
                node,
            )

    def visit_Try(self, node):
        self.validate_body(node)
        if len(node.handlers) + len(node.finalbody) < 1:
            self.invalidate(
                f"{name_of(node)} should have at least one of these: a handler or a finally clause",
                node,
            )
        if len(node.handlers) == 0 and len(node.orelse) != 0:
            self.invalidate(
                f"{name_of(node)} has an else clause but not an exception handler",
                node,
            )

    def visit_ImportFrom(self, node):
        if node.level < 0:
            self.invalidate(
                f"{name_of(node)}'s level should be equal or greater then 0",
                node,
            )
        self.validate_names(node)

    def visit_BoolOp(self, node):
        if len(node.values) < 2:
            self.invalidate(
                f"{name_of(node)} was expecting at least 2 value", node
            )

    def visit_Dict(self, node):
        if len(node.keys) != len(node.values):
            self.invalidate(
                f"{name_of(node)} doesn't have same amount of keys and values",
                node,
            )

    def visit_Compare(self, node):
        if len(node.comparators) == 0:
            self.invalidate(
                f"{name_of(node)} was expecting at least one comparator", node
            )
        if len(node.comparators) != len(node.ops):
            self.invalidate(
                f"{name_of(node)} doesn't have same amount of comparator and operands",
                node,
            )

    def visit_Constant(self, node):
        def is_constant(value):
            if value is None or value is Ellipsis:
                return True
            elif type(value) in CONSTANT_TYPES:
                return True
            elif type(value) in CONSTANT_SEQUENCE_TYPES:
                return all(is_constant(item) for item in value)
            else:
                self.invalidate(
                    f"Non-constant value ({name_of(value)}) encountered inside of a {name_of(node)}",
                    node,
                )

        is_constant(node.value)

    visit_ClassDef = validate_body
    visit_FunctionDef = validate_body
    visit_AsyncFunctionDef = validate_body

    visit_Assign = validate_targets
    visit_Delete = validate_targets

    visit_If = validate_statement
    visit_For = validate_statement
    visit_While = validate_statement

    visit_Global = validate_names
    visit_Import = validate_names

    visit_SetComp = validate_comprehension
    visit_DictComp = validate_comprehension
    visit_ListComp = validate_comprehension
    visit_GeneratorExp = validate_comprehension
