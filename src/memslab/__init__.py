"""Open-source MEMS finite-element teaching laboratory.

A competency-based laboratory sequence built entirely on free software:
GMSH for geometry and meshing, Elmer FEM for the three-dimensional solution,
a pure-Python Morley-element solver as a no-install alternative, and Jupyter
for interpretation.
"""
from .plate import Diaphragm, REFERENCE, REFERENCE_PRESSURE

__version__ = "1.0.0"
__all__ = ["Diaphragm", "REFERENCE", "REFERENCE_PRESSURE"]
