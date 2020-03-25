import ast
from enum import Flag, auto


class Contexts(Flag):
    CLASS = auto()
    GLOBAL = auto()
    FUNCTION = auto()
    COROUTINE = auto()
    GENERATOR = auto()


def context_of(node):
    context = Contexts.GLOBAL
    parent = node
    while parent is not None:
        if isinstance(
            parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            context = Contexts.FUNCTION
            if isinstance(parent, ast.AsyncFunctionDef):
                context |= Contexts.COROUTINE
            break
        elif isinstance(parent, ast.ClassDef):
            context = Contexts.CLASS
            break
        parent = getattr(parent, "parent", None)
    else:
        return context

    if context & Contexts.FUNCTION:
        for node in ast.walk(parent):
            if isinstance(node, ast.Yield) or isinstance(node, ast.YieldFrom):
                context |= Contexts.GENERATOR

    return context


def does_appear_in_parent_chain(node, wanted):
    parent = node
    while parent and not isinstance(parent, wanted):
        parent = getattr(parent, "parent", False)
    return parent
