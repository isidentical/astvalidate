import ast
import copy
import warnings
import weakref
from contextlib import contextmanager
from functools import partialmethod


def name_of(value):
    return type(value).__name__


def _original_getattr(self, attribute):
    raise AttributeError(
        f"'{type(self).__name__}' object has no attribute '{attribute}'"
    )


class ASTValidator(ast.NodeVisitor):
    def visit(self, node):
        super().visit(node)
        if hasattr(self, f"visit_{name_of(node)}"):
            self.generic_visit(node)

    def validate(self, tree):
        self.set_parents(tree)
        try:
            return self.visit(tree)
        finally:
            self.set_parents(tree, clear=True)
            if hasattr(self, "finalize"):
                self.finalize()

    def infer_position(self, node):
        if hasattr(node, "lineno"):
            return node.lineno, node.col_offset
        elif parent := self.closest_positional_node(node):
            return parent.lineno, parent.col_offset
        else:
            return -1, -1

    def invalidate(self, message, node):
        error = SyntaxError(message, (None, *self.infer_position(node), None))
        error.node = node
        raise error

    def warn(self, message, node):
        lineno, _ = self.infer_position(node)
        warnings.warn_explicit(message, SyntaxWarning, "<astvalidate>", lineno)

    def set_parents(self, tree, *, clear=False):
        for parent in ast.walk(tree):
            for children in ast.iter_child_nodes(parent):
                if clear and hasattr(children, "parent"):
                    del children.parent
                else:
                    children.parent = parent

    def closest_positional_node(self, node):
        if not hasattr(node, "parent"):
            return None
        parent = node.parent
        while hasattr(parent, "parent"):
            if hasattr(parent, "lineno"):
                break
            parent = parent.parent
        else:
            return None
        return parent

    def __getattr__(self, attribute):
        if attribute.startswith("Async"):
            real_node = attribute[len("Async") :]
            return getattr(self, real_node)
        raise _original_getattr(self, attribute)


class AsyncAwareASTValidator(ASTValidator):
    def __init__(self, top_level_await=False):
        self.top_level_await = top_level_await

    __getattr__ = partialmethod(_original_getattr)


class ContextAwareASTValidator(ASTValidator):
    def __init__(self):
        self.contexts = []

    def enter_context(self, node):
        self.contexts.append(node)

    def exit_context(self, node):
        self.contexts.pop()

    @property
    def context(self):
        return self.contexts[-1]

    def visit(self, node):
        context_change = isinstance(
            node,
            (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
        if context_change:
            self.enter_context(node)
        super().visit(node)
        if context_change:
            self.exit_context(node)

    def finalize(self):
        self.contexts.clear()
