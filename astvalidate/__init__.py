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


def static_validators(level=None):
    validators = []
    for module_information in pkgutil.iter_modules(
        astvalidate.validators.__path__
    ):
        module_name = f"{VALIDATOR_PKG}.{module_information.name}"
        module = importlib.import_module(module_name)
        for subject in vars(module).values():
            if is_validator(subject) and subject.__module__ == module_name:
                if level is None or subject.LEVEL <= level:
                    validators.append(subject)

    return validators


def dynamic_validators(level=None):
    validators = []
    for validator in ASTValidator.__subclasses__():
        if validator.__module__.startswith(VALIDATOR_PKG) or not is_validator(
            validator
        ):
            continue
        validators.append(validator)
    return validators


def validate(tree, level=None):
    for validator in (*static_validators(level), *dynamic_validators(level)):
        print(validator)
        validator().validate(tree)
    return True
