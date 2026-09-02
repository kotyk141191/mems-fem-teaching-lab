# Contributing

Corrections, additional laboratories and re-anchorings to other devices are
welcome.

## Before opening a pull request

```bash
pip install -e ".[notebooks,dev]"
pytest -q
```

Every test must pass. If a change makes one fail, fix the change rather than the
tolerance — the tests in `tests/test_reference_design.py` assert the numbers
published in the paper, and relaxing one silently decouples the code from it.

## Re-anchoring to a different device

The competency framework and the laboratory scaffold are domain-general. To move
the sequence to a cantilever, an accelerometer or a resonator you need two
things:

1. a geometry template in `src/memslab/geometry.py`, and
2. an analytical reference solution in a module beside `src/memslab/plate.py`.

Laboratory 3 compares against that reference, so it has to exist before the
sequence means anything. Please add tests asserting the reference values, in the
style of `tests/test_reference_design.py`.

## Notebooks

Commit notebooks with outputs cleared:

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

## Style

Plain Python, standard library plus the dependencies already declared. Keep the
no-install path working: a student without Elmer must still be able to run every
notebook.
