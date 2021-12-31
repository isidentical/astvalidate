import importlib
import pkgutil

import astvalidate.validators
from astvalidate.validators.base import ASTValidator

VALIDATOR_PKG = "astvalidate.validators"


def _is_validator(subject):
    return (
        isinstance(subject, type)
        and issubclass(subject, ASTValidator)
        and hasattr(subject, "LEVEL")
    )


def _collect_static_validators():
    for module_information in pkgutil.iter_modules(
        astvalidate.validators.__path__
    ):
        module_name = f"{VALIDATOR_PKG}.{module_information.name}"
        module = importlib.import_module(module_name)
        for subject in vars(module).values():
            if _is_validator(subject) and subject.__module__ == module_name:
                yield subject


def _collect_dynamic_validators():
    yield from filter(_is_validator, ASTValidator.__subclasses__())


def collect_problems(tree, level=None, *, fail_fast=False):
    """
    Iterate through possible SyntaxErrors and SyntaxWarnings for
    the given abstract syntax tree.
    """
    for validator in {
        *_collect_static_validators(),
        *_collect_dynamic_validators(),
    }:
        if level is not None and validator.level > level:
            continue

        yield from validator(fail_fast=fail_fast).validate(tree)


def validate(tree, level=None, *, fail_fast=True):
    """Validate the integrity of the given syntax tree.

    If fail_fast is False, then raise a SyntaxError or
    issue a SyntaxWarning as soon as there is a problem.

    If fail_fast is True, then return a boolean to indicate
    the status of validation. Use astvalidate.collect_errors()
    to retrieve all the problems.
    """

    problems = list(collect_problems(tree, level, fail_fast=fail_fast))
    return not bool(problems)
