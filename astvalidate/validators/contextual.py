import ast

from astvalidate.context import (
    Contexts,
    context_of,
    does_appear_in_parent_chain,
)
from astvalidate.validators.base import AsyncAwareASTValidator, name_of

LEVEL = 2


class ContextualASTValidator(AsyncAwareASTValidator):
    def validate_control_flow(self, node):
        if not does_appear_in_parent_chain(
            node, (ast.For, ast.AsyncFor, ast.While)
        ):
            self.invalidate(
                f"{name_of(node)} should be placed inside of a loop", node
            )

    def validate_async_statement(self, node):
        context = context_of(node)
        if not context & Contexts.COROUTINE and not self.top_level_await:
            self.invalidate(
                f"{name_of(node)} should be placed inside of a coroutine", node
            )

    def visit_Return(self, node):
        context = context_of(node)
        if not context & Contexts.FUNCTION:
            self.invalidate(
                f"{name_of(node)} should be placed inside of a function", node
            )
        if (
            context & Contexts.GENERATOR
            and context & Contexts.COROUTINE
            and node.value is not None
        ):
            self.invalidate(
                f"{name_of(node)} with value can't be part of async generator",
                node,
            )

    def visit_Try(self, node):
        for index, except_handler in enumerate(node.handlers, 1):
            if except_handler.type is None and len(node.handlers) != index:
                self.invalidate(
                    f"{name_of(node)}'s default except must be placed last",
                    node,
                )

    def visit_ImportFrom(self, node):
        if node.module == "__future__" and node.parent.body.index(node) != 0:
            if not (
                isinstance(node.parent.body[-1], ast.Constant)
                and isinstance(node.parent.body[-1].value, str)
            ):
                self.invalidate(
                    "'from __future__' import must occur at the top of file",
                    node,
                )

    visit_Break = validate_control_flow
    visit_Continue = validate_control_flow

    visit_AsyncFor = validate_async_statement
    visit_AsyncWith = validate_async_statement
