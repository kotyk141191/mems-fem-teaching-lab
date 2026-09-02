#!/usr/bin/env python3
"""Generate the synthetic demonstration cohort.

THESE ARE NOT EMPIRICAL DATA. The cohort exists only to show that the analysis
pipeline runs end to end and returns the expected statistics. The generator is
seeded, so the dataset in this repository is exactly reproducible.
"""
import argparse
import csv
import numpy as np

COMPETENCIES = ["C1", "C2", "C3", "C4", "C5", "C6"]
# Plausible pre-test means and the gain each competency is given, by Bloom level.
PRE_MEAN = {"C1": 65, "C2": 50, "C3": 41, "C4": 36, "C5": 43, "C6": 31}
TARGET_GAIN = {"C1": 0.688, "C2": 0.630, "C3": 0.635, "C4": 0.640, "C5": 0.636, "C6": 0.622}


def build(n: int = 28, seed: int = 20260101) -> list[dict]:
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 8, n)          # stable between-student differences
    rows = []
    for i in range(n):
        sid = f"S{i + 1:03d}"
        pre, post = {}, {}
        for c in COMPETENCIES:
            p = np.clip(PRE_MEAN[c] + ability[i] + rng.normal(0, 5), 0, 100)
            q = np.clip(p + TARGET_GAIN[c] * (100 - p) + rng.normal(0, 4), 0, 100)
            pre[c], post[c] = round(float(p), 1), round(float(q), 1)
        rows.append({"student_id": sid, "phase": "pre", **pre})
        rows.append({"student_id": sid, "phase": "post", **post})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", type=int, default=28)
    ap.add_argument("--seed", type=int, default=20260101)
    ap.add_argument("-o", "--out", default="data/synthetic_cohort.csv")
    args = ap.parse_args()
    rows = build(args.n, args.seed)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["student_id", "phase"] + COMPETENCIES)
        wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {len(rows)} rows for {args.n} students to {args.out}")


if __name__ == "__main__":
    main()
