# astvalidate

A series of AST validators for validating the integrity of the given abstract syntax tree.

## API

### `validate(tree: ast.Module, level: Optional[Literal[1, 2, 3]] = None, *, fail_fast: bool = True) -> bool`

`tree` is the AST object that you want to verify. If `fail_fast` is set to `True`, then the found
error or warning will be propagated immediately. If it is set to `False`, `validate()` will return
a boolean response indicating the status of the operation. `level` is an argument to control the
strictness, and turn on/off some of the validators. For a detailed list of validators,
see the table below:

| Validator  | Level | Description                                                       |
| ---------- | ----- | ----------------------------------------------------------------- |
| Syntatical | 1     | Emulates syntax warnings that are normally generated by compiler. |
| Simple     | 1     | Does simple verifications, similar to `PyAST_Validate` interface  |
| Symbolic   | 2     | Emulates syntax error that are normally generated by symbol table |
| Contextual | 3     | Ensures everything is in the right context.                       |

If there are any errors, `validate()` will raise a `SyntaxError` or issue `SyntaxWarnings`
on the location of the target node.

```py
import ast
import astvalidate

tree = ast.parse("""
def func():
    raise ValueError from something
""")
tree.body[0].body[0].exc = None
assert astvalidate.validate(tree)
```

```
File "<string>", line 3
SyntaxError: Raise's cause can't be used without setting an exception
```

### `collect_problems(tree: ast.Module, level: Optional[Literal[1, 2, 3]] = None) -> List[Union[SyntaxError, SyntaxWarning]]`

Same as the `validate`, but instead of returning a boolean response it returns a list of errors/warnings found
in the problematic tree.
