# ASTValidate

A series of AST validators for validating the integrity of the tree.

## Interface
The stable interface is `validate`, which comes directly from the root of
the package. It takes the tree, and the validation level. Validation level
specifies the strictness degree; for an example if it is 1, tree will be only
checked by some basic checks that is similiar to `PyAST_Validate` interface in
`Python/ast.c`. Increasing levels means increasing checks and strictness.

```py
import ast
from astvalidate import validate

tree = ast.parse("def x(): raise X from Y")
assert validate(tree)
```

If the validator encounters with anything that shouldn't be, it raises a `SyntaxError`
with the node's line number and column offset. Also the original node that caused the
error is attached to the exception's `node` attribute.

```py
tree.body[0].body[0].exc = None
assert validate(tree)
```

```
SyntaxError: Raise's cause can't be used without setting an exception
```
