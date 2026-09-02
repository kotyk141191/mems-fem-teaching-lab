"""The released dataset must reproduce the figures quoted in the paper."""
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from memslab.analysis import hake_gain  # noqa: E402

COMP = ["C1", "C2", "C3", "C4", "C5", "C6"]


@pytest.fixture(scope="module")
def cohort():
    return pd.read_csv(ROOT / "data" / "synthetic_cohort.csv")


def test_cohort_shape(cohort):
    assert cohort.student_id.nunique() == 28
    assert set(cohort.phase) == {"pre", "post"}
    assert len(cohort) == 56


def test_overall_gain_matches_the_paper(cohort):
    pre = cohort[cohort.phase == "pre"][COMP].mean().mean()
    post = cohort[cohort.phase == "post"][COMP].mean().mean()
    assert hake_gain(pre, post) == pytest.approx(0.64, abs=0.005)


def test_per_competency_gains_are_in_the_stated_range(cohort):
    pre = cohort[cohort.phase == "pre"]
    post = cohort[cohort.phase == "post"]
    gains = {c: hake_gain(pre[c].mean(), post[c].mean()) for c in COMP}
    assert all(0.60 <= g <= 0.70 for g in gains.values()), gains
    assert min(gains, key=gains.get) == "C6"   # Create, the hardest
    assert max(gains, key=gains.get) == "C1"   # Understand, the highest floor


def test_generator_is_reproducible(tmp_path):
    out = tmp_path / "again.csv"
    subprocess.run([sys.executable, str(ROOT / "data" / "make_synthetic_cohort.py"),
                    "-o", str(out)], check=True, cwd=ROOT)
    assert out.read_text() == (ROOT / "data" / "synthetic_cohort.csv").read_text()


def test_analysis_script_runs(tmp_path):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "analyse_scores.py"),
         str(ROOT / "data" / "synthetic_cohort.csv"), "--figures", str(tmp_path)],
        capture_output=True, text=True, check=True, cwd=ROOT)
    assert "overall normalised gain" in r.stdout
    assert (tmp_path / "fig1_pre_post.png").exists()
    assert (tmp_path / "fig2_normalised_gain.png").exists()
