# Open-source MEMS finite-element teaching laboratory

A competency-based laboratory sequence that teaches finite-element simulation of
microelectromechanical systems on an entirely free toolchain: **GMSH** for
parametric geometry and meshing, **Elmer FEM** for the three-dimensional
solution, a **pure-Python Kirchhoff-plate solver** as a no-install alternative,
and **Jupyter** for interpretation.

Everything here runs on a standard laptop with no commercial licence.

Companion repository to the paper *Free and open-source MEMS simulation tools in
engineering education* (submitted, 2026).

---

## What is here

| Path | What it holds |
|---|---|
| `notebooks/` | The four student-facing laboratories, as executable notebooks |
| `src/memslab/` | Plate model, Morley-element solver, GMSH geometry, gain analysis |
| `instructor/` | Per-student geometry generator and the Elmer solver input |
| `assessment/` | Competency framework, test blueprint, rubric, survey, workbook |
| `data/` | The synthetic demonstration cohort and its seeded generator |
| `scripts/` | One-command analysis of a pre/post scores file |
| `tests/` | Assertions that the code reproduces every number in the paper |

## Install

```bash
git clone https://github.com/kotyk141191/mems-fem-teaching-lab.git
cd mems-fem-teaching-lab
pip install -e ".[notebooks,dev]"
```

Elmer is optional. Without it, every notebook still runs end to end on the
pure-Python solver.

## Check it works

```bash
pytest -q                                       # 18 assertions against the paper
python scripts/analyse_scores.py data/synthetic_cohort.csv
```

The second command prints an overall normalised gain of 0.64 and writes both
summary figures to `figures/`.

## The competency progression

Six competencies, mapped to the Revised Bloom's Taxonomy, across four
laboratories built on a single running example: a clamped square silicon
diaphragm carrying four piezoresistors in a full Wheatstone bridge.

| | Competency | Bloom | Lab |
|---|---|---|---|
| C1 | Explain MEMS transduction and thin-plate mechanics | Understand | 1 |
| C2 | Construct parametric geometry and generate a quality mesh | Apply | 1 |
| C3 | Configure and execute a simulation with correct BCs and loads | Apply | 2 |
| C4 | Verify and validate: convergence, comparison to theory, error | Analyse | 3 |
| C5 | Interpret fields to extract figures of merit and critique them | Evaluate | 4 |
| C6 | Design and optimise a diaphragm to meet a specification | Create | 4 |

## The reference design

`a` = 1000 µm, `h` = 20 µm, `q` = 100 kPa, single-crystal silicon
(E = 169 GPa, ν = 0.28 in the isotropic approximation).

```python
from memslab.plate import REFERENCE, REFERENCE_PRESSURE

d, q = REFERENCE, REFERENCE_PRESSURE
d.w_max(q) * 1e6        # 1.031 um       (w/h = 0.052, small-deflection valid)
d.edge_stress(q)        # 76.9 MPa normal, 21.5 MPa parallel
d.bridge_output(q)      # 38.3 mV/V      (191 mV at a 5 V supply)
d.sensitivity(q) * 1e6  # 0.383 uV/V/Pa
```

The whole chain is eight lines of algebra, so students can evaluate it by hand
before running anything. That is what makes the later numerical result
checkable.

## Individualised student geometries

Each student gets a distinct but comparable design, derived deterministically
from their name, so the class can be regenerated from the roster alone and
answers cannot simply be copied.

```bash
python instructor/generate_variants.py roster.txt -o instructor/variants
```

Change `--seed` between cohorts so variants differ year to year.

## Running an assessment

1. Administer the pre/post test from `assessment/test_blueprint.csv`.
2. Score each laboratory deliverable against `assessment/rubric.csv`.
3. Enter scores in the `Scores` sheet of `assessment/assessment_workbook.xlsx`,
   or in a CSV shaped like `assessment/scores_template.csv`.
4. Run the analysis:

```bash
python scripts/analyse_scores.py my_cohort.csv --real-data
```

You get the Hake normalised gain overall and per competency, a paired-samples
t-test, Cohen's d_z, and both figures. Pass `--real-data` to drop the
"illustrative data" label the synthetic dataset carries.

## About the synthetic dataset

`data/synthetic_cohort.csv` holds **28 synthetic records, not empirical data**.
No cohort has yet been taught with these materials. The dataset exists to show
that the analysis pipeline runs end to end and returns the expected statistics,
and it is labelled as such wherever it appears. The generator is seeded, so the
file regenerates byte-for-byte.

## A note on the convergence study

Laboratory 3 makes a point worth stating here, because it surprised us. Refine
the mesh far enough and the error against the closed-form solution stops
falling — around 0.5% for the central deflection. That floor is not the mesh.
The tabulated plate coefficient α = 0.00126 is quoted to three significant
figures, and Richardson extrapolation of the computed sequence gives
α ≈ 0.001265. Once discretisation error drops below the precision of the number
you are comparing against, you are measuring the reference, not the model.

`tests/test_reference_design.py::test_richardson_limit_exposes_the_tabulated_coefficient_precision`
asserts it, so the lesson cannot quietly rot.

## Licensing

Dual, by directory:

- **Code** (`src/`, `scripts/`, `tests/`, the two generator scripts) — MIT, see `LICENSE`
- **Teaching materials** (`notebooks/`, `assessment/`, laboratory documentation) — CC BY 4.0, see `LICENSE-CC-BY-4.0.md`

## Citing

See `CITATION.cff`, or use the "Cite this repository" button on GitHub.

**Mykhailo Kotyk** — Department of Computer Engineering and Electronics,
Vasyl Stefanyk Precarpathian National University, Ivano-Frankivsk, Ukraine
[ORCID 0000-0001-6149-0734](https://orcid.org/0000-0001-6149-0734)

## Acknowledgements

Viktor Kukuruza contributed to the implementation of the laboratory notebooks
and the verification of the solver paths against the analytical solutions.
