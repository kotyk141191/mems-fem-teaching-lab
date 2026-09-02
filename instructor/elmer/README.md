# Elmer path

The three-dimensional solution uses [Elmer FEM](https://www.elmerfem.org).
Both solver paths report the same quantities and take the same boundary
conditions and loads, so a notebook written against one runs against the other.

## Running

```bash
gmsh -3 ../variants/<student>.geo -o diaphragm.msh
ElmerGrid 14 2 diaphragm.msh -autoclean
ElmerSolver diaphragm.sif
```

`diaphragm.vtu` opens in ParaView.

## If Elmer is not installed

Use the no-install path instead. It needs nothing beyond the Python
dependencies in `requirements.txt`:

```python
from memslab.plate import REFERENCE, REFERENCE_PRESSURE
from memslab.morley import solve_clamped_square

result = solve_clamped_square(REFERENCE, REFERENCE_PRESSURE, refine=5)
print(result["w_max"] * 1e6, "um")
```

## Boundary numbering

The `.geo` templates extrude a plane surface, so GMSH numbers the four side
faces 1-4, the bottom 5 and the top 6. Check with `gmsh diaphragm.msh` before
trusting the numbering on a geometry you have modified.
