"""Pure-Python Kirchhoff plate solver on the non-conforming Morley triangle.

This is the no-install path referred to in the paper: it needs only scikit-fem,
so every notebook runs during class without an Elmer installation. It solves the
same problem as the Elmer path, imposes the same boundary conditions and reports
the same quantities.

Reference: Gustafsson, T., & McBain, G. D. (2020). scikit-fem: A Python package
for finite element assembly. Journal of Open Source Software, 5(52), 2369.
"""
from __future__ import annotations

import numpy as np
from skfem import (Basis, BilinearForm, LinearForm, MeshTri, ElementTriMorley,
                   asm, condense, solve)
from skfem.helpers import ddot, dd, trace

from .plate import Diaphragm


def _bilinear(nu: float):
    @BilinearForm
    def a(u, v, _):
        return (1.0 - nu) * ddot(dd(u), dd(v)) + nu * trace(dd(u)) * trace(dd(v))
    return a


def _load(q: float):
    @LinearForm
    def L(v, _):
        return q * v
    return L


def solve_clamped_square(plate: Diaphragm, q: float, refine: int = 4):
    """Solve the clamped square plate and return the discrete solution.

    Discretises the weak form of Equation (1) with the Morley element,
    Equation (10). Every boundary degree of freedom is set to zero, which
    imposes w = 0 and dw/dn = 0 exactly.

    Returns a dict with the mesh, the basis, the deflection vector, the peak
    deflection, the recovered peak surface stress and the degree-of-freedom
    count.
    """
    mesh = MeshTri().refined(refine).scaled([plate.a, plate.a])
    basis = Basis(mesh, ElementTriMorley())

    K = asm(_bilinear(plate.nu), basis)
    f = asm(_load(q / plate.D), basis)          # w'' scaled by 1/D
    boundary = basis.get_dofs()
    w = solve(*condense(K, f, D=boundary))

    # Bending moments recovered element-wise from the per-element Hessian,
    # then converted to surface stress through Equation (5).
    hess_basis = basis.with_element(ElementTriMorley())
    dofs = hess_basis.element_dofs
    H = dd(hess_basis.interpolate(w))
    kxx, kyy = np.asarray(H[0][0]), np.asarray(H[1][1])
    m_xx = plate.D * (kxx + plate.nu * kyy)
    sigma = 6.0 * np.abs(m_xx) / plate.h ** 2

    return {
        "mesh": mesh,
        "basis": basis,
        "w": w,
        "w_max": float(np.abs(w[basis.nodal_dofs]).max()),
        "sigma_max": float(sigma.max()),
        "ndof": int(basis.N),
        "h_char": float(plate.a / (2 ** refine)),
    }


def convergence_study(plate: Diaphragm, q: float, refinements=(2, 3, 4, 5)):
    """Run the Laboratory 3 mesh-convergence study.

    Returns a list of records with the characteristic mesh size, the number of
    degrees of freedom, the computed deflection and stress, and the relative
    error against the closed-form reference, Equation (9).
    """
    w_ref = plate.w_max(q)
    s_ref, _ = plate.edge_stress(q)
    out = []
    for r in refinements:
        res = solve_clamped_square(plate, q, refine=r)
        out.append({
            "refine": r,
            "h_char_um": res["h_char"] * 1e6,
            "ndof": res["ndof"],
            "w_max_um": res["w_max"] * 1e6,
            "eps_w": abs(res["w_max"] - w_ref) / w_ref,
            "sigma_max_MPa": res["sigma_max"] / 1e6,
            "eps_sigma": abs(res["sigma_max"] - s_ref) / s_ref,
        })
    return out
