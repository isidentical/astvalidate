import importlib
import pkgutil

import astvalidate.validators
from astvalidate.validators.base import ASTValidator

VALIDATOR_PKG = "astvalidate.validators"


def is_validator(subject):
    return (
        isinstance(subject, type)
        and issubclass(subject, ASTValidator)
        and hasattr(subject, "LEVEL")
    )


def static_validators():
    for module_information in pkgutil.iter_modules(
        astvalidate.validators.__path__
    ):
        module_name = f"{VALIDATOR_PKG}.{module_information.name}"
        module = importlib.import_module(module_name)
        for subject in vars(module).values():
            if is_validator(subject) and subject.__module__ == module_name:
                yield subject


def dynamic_validators():
    yield from filter(is_validator, ASTValidator.__subclasses__())


def validate(tree, level=None):
    for validator in {*static_validators(), *dynamic_validators()}:
        if level is not None and validator.level > level:
            continue
        validator().validate(tree)

    return True
