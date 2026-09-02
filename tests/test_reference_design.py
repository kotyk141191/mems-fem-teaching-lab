"""The reference design must reproduce the numbers quoted in the paper.

If any of these fail, either the code or the paper is wrong. Do not relax a
tolerance to make a test pass.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from memslab.plate import Diaphragm, REFERENCE as D, REFERENCE_PRESSURE as Q  # noqa: E402
from memslab.morley import solve_clamped_square, convergence_study  # noqa: E402
from memslab.analysis import hake_gain, paired_stats, richardson_limit  # noqa: E402


def test_flexural_rigidity():
    assert D.D == pytest.approx(1.2225e-4, rel=1e-3)


def test_central_deflection():
    assert D.w_max(Q) * 1e6 == pytest.approx(1.03, abs=5e-3)


def test_small_deflection_criterion_holds():
    assert D.w_max(Q) / D.h == pytest.approx(0.052, abs=1e-3)
    assert D.small_deflection_ok(Q)


def test_edge_stress():
    s_l, s_t = D.edge_stress(Q)
    assert s_l / 1e6 == pytest.approx(76.9, abs=0.1)
    assert s_t / 1e6 == pytest.approx(21.5, abs=0.1)


def test_resistance_change():
    long_arm, trans_arm = D.resistance_change(Q)
    assert long_arm * 100 == pytest.approx(4.10, abs=0.02)
    assert trans_arm * 100 == pytest.approx(-3.55, abs=0.02)


def test_bridge_output_and_sensitivity():
    assert D.bridge_output(Q) * 1e3 == pytest.approx(38.3, abs=0.1)
    assert D.bridge_output(Q) * 5 * 1e3 == pytest.approx(191, abs=1.0)
    assert D.sensitivity(Q) * 1e6 == pytest.approx(0.383, abs=1e-3)


def test_thinner_diaphragm_is_more_sensitive():
    thin = Diaphragm(a=D.a, h=D.h / 2)
    assert thin.sensitivity(Q) > D.sensitivity(Q)
    assert thin.edge_stress(Q)[0] > D.edge_stress(Q)[0]


def test_morley_converges_towards_the_analytical_deflection():
    errs = [r["eps_w"] for r in convergence_study(D, Q, refinements=(3, 4, 5))]
    assert errs == sorted(errs, reverse=True), "error must fall under refinement"
    assert errs[-1] < 0.03


def test_morley_converges_towards_the_analytical_stress():
    errs = [r["eps_sigma"] for r in convergence_study(D, Q, refinements=(3, 4, 5))]
    assert errs == sorted(errs, reverse=True)
    assert errs[-1] < 0.02


def test_richardson_limit_exposes_the_tabulated_coefficient_precision():
    """The residual disagreement is the reference's precision, not the mesh.

    Extrapolating the computed sequence gives alpha ~ 0.001265, while the
    tabulated coefficient is quoted as 0.00126. This is the point Laboratory 3
    makes, so the repository asserts it.
    """
    ws = [r["w_max_um"] for r in convergence_study(D, Q, refinements=(4, 5, 6))]
    limit = richardson_limit(ws) * 1e-6
    alpha_implied = limit * D.D / (Q * D.a ** 4)
    assert alpha_implied == pytest.approx(0.001265, abs=5e-6)
    assert abs(alpha_implied - 0.00126) / 0.00126 > 2e-3


def test_clamped_boundary_is_fully_constrained():
    res = solve_clamped_square(D, Q, refine=3)
    boundary = res["basis"].get_dofs()
    assert np.allclose(res["w"][boundary], 0.0, atol=1e-14)


def test_hake_gain():
    assert hake_gain(40.0, 70.0) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        hake_gain(100.0, 100.0)


def test_paired_stats():
    rng = np.random.default_rng(0)
    pre = rng.normal(50, 10, 30)
    st = paired_stats(pre, pre + 20)
    assert st["n"] == 30
    assert st["mean_diff"] == pytest.approx(20.0)
    assert st["p"] < 1e-6
