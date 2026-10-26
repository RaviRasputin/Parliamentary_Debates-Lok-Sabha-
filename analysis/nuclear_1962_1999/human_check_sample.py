"""Draw the 200-passage human check: 50 per voice, spread across the six eras, random within
cells, from the 2,954 model-coded passages (gold.csv + gold2.csv). The human codes blind (text only)."""
import csv, json, random, sys
from collections import defaultdict
from pathlib import Path

VAL, DOCS = Path(sys.argv[1]), Path(sys.argv[2])
SEED = 20261101
ERAS = [("1962-68", 1962, 1968), ("1969-79", 1969, 1979), ("1980-89", 1980, 1989),
        ("1990-93", 1990, 1993), ("1994-97", 1994, 1997), ("1998-99", 1998, 1999)]
era_of = lambda y: next(e for e, a, b in ERAS if a <= y <= b)
meta = {}
for name in ("sample.csv", "sample2.csv"):
    for r in csv.DictReader(open(VAL / name, encoding="utf-8")):
        meta[r["code_id"]] = r
cells = defaultdict(list)
for name in ("gold.csv", "gold2.csv"):
    for g in csv.DictReader(open(VAL / name, encoding="utf-8")):
        m = meta[g["code_id"]]
        if m["voice"] != "near_miss":
            cells[(m["voice"], era_of(int(m["year"])))].append(g["code_id"])
rnd = random.Random(SEED)
picked = []
for v in ("LS_member", "RS_member", "minister", "MEA"):
    quota = [9, 9, 8, 8, 8, 8]  # 50 per voice
    for (e, _, _), q in zip(ERAS, quota):
        pool = sorted(cells[(v, e)])
        picked += [(c, v, e) for c in rnd.sample(pool, min(q, len(pool)))]
rnd.shuffle(picked)
with open(VAL / "human_check_sample.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["check_id", "code_id", "voice", "era"])
    for i, (c, v, e) in enumerate(picked, 1):
        w.writerow([f"H{i:03d}", c, v, e])
DOCS.mkdir(parents=True, exist_ok=True)
for i, (c, v, e) in enumerate(picked, 1):
    json.dump({"code_id": f"H{i:03d}", "text": meta[c]["text"], "batches": ["check"]},
              open(DOCS / f"H{i:03d}.json", "w"))
print(len(picked), "passages")
