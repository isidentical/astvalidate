import __future__

import ast
import struct

from astvalidate.context import (
    Contexts,
    context_of,
    does_appear_in_parent_chain,
)
from astvalidate.validators.base import AsyncAwareASTValidator, name_of

INT_MAX = 2 ** (struct.calcsize("i") * 8 - 1) - 1


class ContextualASTValidator(AsyncAwareASTValidator):
    LEVEL = 3

    def validate_yield(self, node):
        context = context_of(node)
        if not context & Contexts.FUNCTION:
            self.invalidate(
                f"{name_of(node)} should be placed inside of a function", node
            )

    def validate_assignment(self, node):
        seen_star = False
        for index, target in enumerate(node.targets):
            if isinstance(target, ast.Starred) and not seen_star:
                if index >= (1 << 8) or len(node.targets) - index - 1 >= (
                    INT_MAX >> 8
                ):
                    self.invalidate(
                        f"Too many expressions used with star unpacking with {name_of(node)}",
                        node,
                    )
                seen_star = True
            elif isinstance(target, ast.Starred) and seen_star:
                self.invalidate(
                    f"More then one starred expressions can't be placed together in {name_of(node)}",
                    node,
                )

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
        if node.module == "__future__":
            if node.parent.body.index(node) != 0 and not (
                isinstance(node.parent.body[-1], ast.Constant)
                and isinstance(node.parent.body[-1].value, str)
            ):
                self.invalidate(
                    "'from __future__' import must occur at the top of file",
                    node,
                )

            for future in node.names:
                if future.name not in __future__.all_feature_names:
                    self.invalidate(
                        f"Future feature '{future.name}' is not defined", node
                    )

    def visit_comprehension(self, node):
        if node.is_async:
            self.validate_async_statement(node)

    def visit_YieldFrom(self, node):
        self.validate_yield(node)
        if context_of(node) & Contexts.COROUTINE:
            self.invalidate(
                f"{name_of(node)} can't be used in a coroutine", node
            )

    def visit_Await(self, node):
        self.validate_yield(node)
        self.validate_async_statement(node)

    visit_Yield = validate_yield

    visit_Assign = validate_assignment

    visit_Break = validate_control_flow
    visit_Continue = validate_control_flow

    visit_AsyncFor = validate_async_statement
    visit_AsyncWith = validate_async_statement
