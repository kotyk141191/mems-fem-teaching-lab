#!/usr/bin/env python3
"""Single-command analysis of a pre/post scores file.

Computes the Hake normalised gain overall and per competency, a paired-samples
t-test and Cohen's d_z, and writes the two summary figures. A real cohort's
gradebook drops in unchanged, provided it has the columns of
assessment/scores_template.csv.

    python scripts/analyse_scores.py data/synthetic_cohort.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from memslab.analysis import hake_gain, gain_band, paired_stats  # noqa: E402

COMPETENCIES = ["C1", "C2", "C3", "C4", "C5", "C6"]
BLOOM = ["Understand", "Apply", "Apply", "Analyse", "Evaluate", "Create"]
INK, ACCENT, MUTED = "#1a1a1a", "#1f6f8b", "#b8bec4"


def load(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path)
    missing = {"student_id", "phase"} - set(df.columns)
    if missing:
        raise SystemExit(f"missing column(s): {', '.join(sorted(missing))}")
    pre = df[df.phase == "pre"].set_index("student_id")[COMPETENCIES].sort_index()
    post = df[df.phase == "post"].set_index("student_id")[COMPETENCIES].sort_index()
    if not pre.index.equals(post.index):
        raise SystemExit("every student needs exactly one pre and one post row")
    return pre, post


def figures(pre: pd.DataFrame, post: pd.DataFrame, gains: dict, outdir: Path,
            illustrative: bool) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    labels = [f"{c}\n{b}" for c, b in zip(COMPETENCIES, BLOOM)]
    tag = " (illustrative data)" if illustrative else ""

    x = np.arange(len(COMPETENCIES))
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
    ax.bar(x - 0.2, pre.mean(), 0.4, label="pre", color=MUTED)
    ax.bar(x + 0.2, post.mean(), 0.4, label="post", color=ACCENT)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("mean score [%]"); ax.set_ylim(0, 100)
    ax.set_title(f"Pre/post by competency{tag}", fontsize=10, color=INK)
    ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(outdir / "fig1_pre_post.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
    ax.bar(x, [gains[c] for c in COMPETENCIES], 0.55, color="#1b6b52")
    for y, lab in ((0.3, "medium"), (0.7, "high")):
        ax.axhline(y, ls="--", lw=0.8, color=MUTED)
        ax.text(len(x) - 0.4, y + 0.012, lab, fontsize=7, color=MUTED)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("normalised gain $\\langle g \\rangle$"); ax.set_ylim(0, 1)
    ax.set_title(f"Normalised gain across the Bloom progression{tag}",
                 fontsize=10, color=INK)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(outdir / "fig2_normalised_gain.png"); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores", type=Path)
    ap.add_argument("--figures", type=Path, default=Path("figures"))
    ap.add_argument("--real-data", action="store_true",
                    help="omit the 'illustrative data' label from the figures")
    args = ap.parse_args()

    pre, post = load(args.scores)
    gains = {c: hake_gain(pre[c].mean(), post[c].mean()) for c in COMPETENCIES}
    overall = hake_gain(pre.mean().mean(), post.mean().mean())
    st = paired_stats(pre.mean(axis=1).to_numpy(), post.mean(axis=1).to_numpy())

    print(f"cohort: n = {st['n']}   source: {args.scores}")
    if not args.real_data:
        print("NOTE: figures are labelled as illustrative; pass --real-data for a real cohort.")
    print(f"\noverall normalised gain  <g> = {overall:.2f}  ({gain_band(overall)})")
    print(f"{'':<4}{'pre':>8}{'post':>8}{'<g>':>8}  band")
    for c in COMPETENCIES:
        print(f"{c:<4}{pre[c].mean():>8.1f}{post[c].mean():>8.1f}"
              f"{gains[c]:>8.2f}  {gain_band(gains[c])}")
    print(f"\npaired t({st['df']}) = {st['t']:.2f}, p = {st['p']:.2e}, "
          f"Cohen's d_z = {st['cohens_dz']:.2f}")
    print(f"mean difference = {st['mean_diff']:.1f} points (SD {st['sd_diff']:.1f})")

    figures(pre, post, gains, args.figures, illustrative=not args.real_data)
    print(f"\nfigures written to {args.figures}/")


if __name__ == "__main__":
    main()
