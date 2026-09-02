#!/usr/bin/env python3
"""Generate one reproducible diaphragm variant per student, plus the index.

    python instructor/generate_variants.py roster.txt -o instructor/variants

`roster.txt` holds one student name per line. The same name always produces the
same geometry, so the whole class can be regenerated from the roster alone.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from memslab.geometry import write_class  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roster", type=Path, help="one student name per line")
    ap.add_argument("-o", "--out", type=Path, default=Path("instructor/variants"))
    ap.add_argument("--seed", default="mems-lab-2026",
                    help="change per cohort so variants differ year to year")
    args = ap.parse_args()

    names = [ln.strip() for ln in args.roster.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    if not names:
        raise SystemExit(f"{args.roster} is empty")
    index = write_class(names, args.out, seed=args.seed)
    print(f"wrote {len(names)} .geo files to {args.out}/")
    print(f"index: {index}")


if __name__ == "__main__":
    main()
