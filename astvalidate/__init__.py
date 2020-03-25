import importlib
import pkgutil

import astvalidate.validators

IGNORE = -1


def discover_validators(level):
    validators = []
    for module_information in pkgutil.iter_modules(
        astvalidate.validators.__path__
    ):
        module = importlib.import_module(
            f"astvalidate.validators.{module_information.name}"
        )
        if hasattr(module, "LEVEL") and (
            module.LEVEL <= level or level == IGNORE
        ):
            validators.append(
                getattr(
                    module, f"{module_information.name.title()}ASTValidator"
                )
            )

    return validators


def validate(tree, level=IGNORE):
    for validator in discover_validators(level):
        validator().validate(tree)

    return True
