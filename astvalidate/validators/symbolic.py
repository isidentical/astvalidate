import ast
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Flag, auto
from functools import partial, partialmethod
from typing import DefaultDict

from astvalidate.validators.base import ContextAwareASTValidator, name_of


class ScopeDeclarations(Flag):
    NONE = auto()
    LOCAL = auto()
    GLOBAL = auto()
    NONLOCAL = auto()


ANY_SCOPE = ScopeDeclarations.GLOBAL | ScopeDeclarations.NONLOCAL


@dataclass
class STE:
    node: ast.AST
    names: DefaultDict[str, ScopeDeclarations] = field(
        default_factory=partial(defaultdict, lambda: ScopeDeclarations.NONE)
    )


class SymbolicASTValidator(ContextAwareASTValidator):
    LEVEL = 2

    def enter_context(self, node):
        self.contexts.append(STE(node))

    def exit_context(self, node):
        self.validate_ste(self.contexts.pop())

    def set_scope(self, node, scope):
        for name in node.names:
            if self.context.names[name] & ScopeDeclarations.LOCAL:
                self.invalidate(
                    f"'{name}' can't be used before the global/nonlocal declaration",
                    node,
                )
            self.context.names[name] |= scope

    def visit_Name(self, node):
        name = node.id
        if self.context.names[name] is ScopeDeclarations.NONE:
            self.context.names[name] = ScopeDeclarations.LOCAL

    visit_Global = partialmethod(set_scope, scope=ScopeDeclarations.GLOBAL)
    visit_Nonlocal = partialmethod(set_scope, scope=ScopeDeclarations.NONLOCAL)

    def visit_arguments(self, node):
        args = [
            *node.posonlyargs,
            *node.args,
            node.vararg,
            *node.kwonlyargs,
            node.kwarg,
        ]
        seen = set()
        for arg in args:
            if arg is None:
                continue

            if arg.arg in seen:
                self.invalidate(
                    f"Argument '{arg.arg}' is duplicated.", node.parent
                )
            seen.add(arg.arg)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            target = node.target.id
            if self.context.names[target] & ANY_SCOPE:
                self.invalidate(
                    f"Annotated name '{target}' can't be used with global/nonlocal",
                    node,
                )

    def visit_ImportFrom(self, node):
        if not isinstance(self.context.node, ast.Module) and any(
            alias.name == "*" for alias in node.names
        ):
            self.invalidate(
                f"Star import can only be used at the module level", node
            )

    def validate_ste(self, ste):
        for name, scope in ste.names.items():
            if (
                scope & ScopeDeclarations.GLOBAL
                and scope & ScopeDeclarations.NONLOCAL
            ):
                self.invalidate(
                    f"'{name}' can't be both nonlocal and global", ste.node
                )
            if (
                isinstance(ste.node, ast.Module)
                and scope & ScopeDeclarations.NONLOCAL
            ):
                self.invalidate(
                    f"'{name}' can't be declared as nonlocal on module level",
                    ste.node,
                )

    def finalize(self):
        self.contexts.clear()
