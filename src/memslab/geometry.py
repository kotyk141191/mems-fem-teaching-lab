"""Parametric GMSH geometry and reproducible per-student variants."""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class Variant:
    student: str
    shape: str        # square | rectangular | circular
    a_um: float       # side length, or diameter for a circular membrane
    b_um: float       # second side; equals a_um for square and circular
    h_um: float


SHAPES = ("square", "rectangular", "circular")


def variant_for(student: str, seed: str = "mems-lab-2026") -> Variant:
    """Deterministic geometry for one student.

    The same name always yields the same design, so the instructor can
    regenerate the whole class from the roster alone.
    """
    digest = hashlib.sha256(f"{seed}:{student}".encode()).digest()
    shape = SHAPES[digest[0] % 3]
    a = 800.0 + (digest[1] % 9) * 50.0          # 800-1200 um
    b = a if shape != "rectangular" else a * (0.6 + (digest[2] % 5) * 0.1)
    h = 15.0 + (digest[3] % 7) * 2.5            # 15-30 um
    return Variant(student, shape, round(a, 1), round(b, 1), round(h, 1))


def geo_source(v: Variant, mesh_size_um: float = 40.0) -> str:
    """GMSH .geo source for one variant."""
    if v.shape == "circular":
        body = (f"r = {v.a_um / 2};\n"
                f"Point(1) = {{0, 0, 0, lc}};\n"
                f"Point(2) = {{ r, 0, 0, lc}};\n"
                f"Point(3) = {{0,  r, 0, lc}};\n"
                f"Point(4) = {{-r, 0, 0, lc}};\n"
                f"Point(5) = {{0, -r, 0, lc}};\n"
                "Circle(1) = {2,1,3}; Circle(2) = {3,1,4};\n"
                "Circle(3) = {4,1,5}; Circle(4) = {5,1,2};\n"
                "Curve Loop(1) = {1,2,3,4};\n")
    else:
        body = (f"a = {v.a_um}; b = {v.b_um};\n"
                "Point(1) = {0, 0, 0, lc};\n"
                "Point(2) = {a, 0, 0, lc};\n"
                "Point(3) = {a, b, 0, lc};\n"
                "Point(4) = {0, b, 0, lc};\n"
                "Line(1) = {1,2}; Line(2) = {2,3};\n"
                "Line(3) = {3,4}; Line(4) = {4,1};\n"
                "Curve Loop(1) = {1,2,3,4};\n")
    return (f"// Diaphragm variant for {v.student}\n"
            f"// shape={v.shape}  a={v.a_um} um  b={v.b_um} um  h={v.h_um} um\n"
            'SetFactory("OpenCASCADE");\n'
            f"lc = {mesh_size_um};\n{body}"
            "Plane Surface(1) = {1};\n"
            f"Extrude {{0, 0, {v.h_um}}} {{ Surface{{1}}; Layers{{2}}; Recombine; }}\n"
            'Physical Volume("diaphragm") = {1};\n')


def write_class(students: list[str], outdir: str | Path,
                seed: str = "mems-lab-2026") -> Path:
    """Write one .geo per student plus the index that records who got what."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    variants = [variant_for(s, seed) for s in students]
    for v in variants:
        slug = v.student.lower().replace(" ", "_")
        (outdir / f"{slug}.geo").write_text(geo_source(v), encoding="utf-8")
    index = outdir / "variant_index.csv"
    with index.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(asdict(variants[0])))
        wr.writeheader()
        for v in variants:
            wr.writerow(asdict(v))
    return index
