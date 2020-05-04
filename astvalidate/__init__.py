import importlib
import pkgutil

import astvalidate.validators


def discover_validators(level=None):
    validators = []
    for module_information in pkgutil.iter_modules(
        astvalidate.validators.__path__
    ):
        module = importlib.import_module(
            f"astvalidate.validators.{module_information.name}"
        )
        if hasattr(module, "LEVEL") and (
            level is None or module.LEVEL <= level
        ):
            validators.append(
                getattr(
                    module, f"{module_information.name.title()}ASTValidator"
                )
            )

    return validators


def validate(tree, level=None):
    for validator in discover_validators(level):
        validator().validate(tree)
    else:
        return True
