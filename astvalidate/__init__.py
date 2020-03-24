from astvalidate.simple import SimpleASTValidator

VALIDATORS = [SimpleASTValidator()]


def validate(tree, level=1):
    if not 0 <= level <= len(VALIDATORS):
        raise ValueError("Level should be in range of 0..{len(VALIDATORS)}")

    for validator in VALIDATORS[:level]:
        validator.validate(tree)

    return True
