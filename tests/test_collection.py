import ast

import astvalidate

PROBLEMATIC_SOURCE = """
return something

def perhaps():
    assert ([](), 'msg') # list call

nonlocal perhaps
"""


def test_ast_validation_multiple_issues():
    node = ast.parse(PROBLEMATIC_SOURCE)
    assert not astvalidate.validate(node, fail_fast=False)


def test_collect_problems():
    node = ast.parse(PROBLEMATIC_SOURCE)
    problems = astvalidate.collect_problems(node, fail_fast=False)
    assert len(list(problems)) == 4
