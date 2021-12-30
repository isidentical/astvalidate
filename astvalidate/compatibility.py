import ast
import sys

PY39_PLUS = sys.version_info >= (3, 9)


def slice_value(value, /):
    if PY39_PLUS or isinstance(value, ast.Slice):
        return value
    elif isinstance(value, ast.Index):
        return value.value
    elif isinstance(value, ast.ExtSlice):
        extslice = ast.Tuple(elts=value.dims, ctx=ast.Load())
        ast.copy_location(extslice)
        return extslice
    else:
        raise ValueError(f"Invalid slice, {ast.dump(value)}!")
