#!/usr/bin/env python3
"""
Stage 2 — Arrange the downloaded PDFs by year.

Each debate PDF carries its sitting date in the filename, e.g.
``lsd_01_01_13-05-1952.pdf`` -> 13 May 1952. This script reads that date and
sorts every PDF into a per-year folder, which is the organising key for the
whole archive.

    python scripts/2_arrange_by_year.py --in pdfs/ --out by_year/

Use --move to move files instead of copying them.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

# Matches a DD-MM-YYYY date anywhere in the filename (the sitting date).
DATE_RE = re.compile(r"(\d{2})-(\d{2})-(\d{4})")


def year_of(filename: str) -> int | None:
    m = DATE_RE.search(filename)
    if not m:
        return None
    day, month, year = (int(g) for g in m.groups())
    if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
        return year
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Sort debate PDFs into per-year folders.")
    ap.add_argument("--in", dest="src", type=Path, default=Path("pdfs"))
    ap.add_argument("--out", dest="dst", type=Path, default=Path("by_year"))
    ap.add_argument("--move", action="store_true", help="move instead of copy")
    args = ap.parse_args()

    sorted_count = unmatched = 0
    for pdf in sorted(args.src.glob("*.pdf")):
        year = year_of(pdf.name)
        if year is None:
            print(f"  ! could not read a date from {pdf.name} — skipping")
            unmatched += 1
            continue
        target_dir = args.dst / str(year)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / pdf.name
        if args.move:
            shutil.move(str(pdf), target)
        else:
            shutil.copy2(pdf, target)
        sorted_count += 1

    print(f"\nDone. arranged={sorted_count} unmatched={unmatched} -> {args.dst}/")


if __name__ == "__main__":
    main()
