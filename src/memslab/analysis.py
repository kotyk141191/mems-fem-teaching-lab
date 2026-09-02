"""Learning-gain analysis: Hake normalised gain, paired t-test, effect size."""
from __future__ import annotations

import numpy as np
from scipy import stats


def hake_gain(pre_mean: float, post_mean: float) -> float:
    """Class normalised gain from mean percentage scores, Equation (11).

    Hake, R. R. (1998). American Journal of Physics, 66(1), 64-74.
    """
    if pre_mean >= 100.0:
        raise ValueError("pre-test mean of 100% leaves no room for gain")
    return (post_mean - pre_mean) / (100.0 - pre_mean)


def gain_band(g: float) -> str:
    """Hake's conventional bands."""
    return "high" if g >= 0.7 else ("medium" if g >= 0.3 else "low")


def paired_stats(pre: np.ndarray, post: np.ndarray) -> dict:
    """Paired-samples t-test and Cohen's d_z, Equation (12)."""
    pre, post = np.asarray(pre, float), np.asarray(post, float)
    if pre.shape != post.shape:
        raise ValueError("pre and post must have the same shape")
    d = post - pre
    n = d.size
    sd = d.std(ddof=1)
    t, p = stats.ttest_rel(post, pre)
    return {
        "n": n,
        "mean_diff": float(d.mean()),
        "sd_diff": float(sd),
        "t": float(t),
        "p": float(p),
        "df": n - 1,
        "cohens_dz": float(d.mean() / sd) if sd > 0 else float("nan"),
    }


def richardson_limit(values: list[float]) -> float:
    """Extrapolate a monotone, uniformly refined sequence to its limit.

    Used in Laboratory 3 to estimate the converged value and so to separate
    discretisation error from the precision of the analytical reference.
    """
    if len(values) < 3:
        raise ValueError("need at least three successively refined values")
    f2, f1, f0 = values[-3], values[-2], values[-1]
    r = (f0 - f1) / (f1 - f2)
    if not 0 < r < 1:
        return f0
    return f0 + (f0 - f1) * r / (1.0 - r)
