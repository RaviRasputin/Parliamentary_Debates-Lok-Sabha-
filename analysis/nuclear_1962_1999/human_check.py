"""Compare the author's blind human-check codes with the adjudicated model codes.

Usage: python3 -I human_check.py VALDIR CODES_DIR [SAMPLE_CSV BATCH OUT_PREFIX [weapons|broad]]
  defaults: human_check_sample.csv check human_check; relevant-only set: human_check2_sample.csv check2 human_check2
  VALDIR    validation folder (human_check_sample.csv, gold.csv, gold2.csv)
  CODES_DIR the coding page's exported documents, i.e. CODES_DIR/codes/H###.json
            (ArtifactData "list" of collection "codes" with out_dir=CODES_DIR)
Model relevance follows codebook v1.1 (weapons and security only) unless "broad" is given.
Writes VALDIR/human_check_results.csv and VALDIR/human_check_agreement.csv.
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

VAL, CODES = Path(sys.argv[1]), Path(sys.argv[2])
SAMPLE, BATCH, PREFIX = (sys.argv[3:6] if len(sys.argv) > 5 else ("human_check_sample.csv", "check", "human_check"))
WEAPON_STANCES = {"pro_bomb", "keep_option", "disarmament", "critical_of_tests"}
WEAPON_FRAMES = ["disarmament", "option_open", "discrimination", "deterrence_weapon", "security_threat"]
SCOPE = sys.argv[6] if len(sys.argv) > 6 else "weapons"
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]


def alpha_nominal(units):
    """Krippendorff's alpha, nominal; units = list of value lists (one per coder)."""
    pairs = Counter()
    for vals in units:
        vals = [v for v in vals if v not in (None, "")]
        m = len(vals)
        if m < 2:
            continue
        for i, a in enumerate(vals):
            for j, b in enumerate(vals):
                if i != j:
                    pairs[(a, b)] += 1 / (m - 1)
    n_c = Counter()
    for (a, _), w in pairs.items():
        n_c[a] += w
    n = sum(n_c.values())
    if n <= 1:
        return float("nan")
    d_o = sum(w for (a, b), w in pairs.items() if a != b) / n
    d_e = sum(n_c[a] * n_c[b] for a in n_c for b in n_c if a != b) / (n * (n - 1))
    return 1.0 if d_e == 0 else 1 - d_o / d_e


gold = {}
for name in ("gold.csv", "gold2.csv"):
    for g in csv.DictReader(open(VAL / name, encoding="utf-8")):
        if SCOPE == "weapons" and g["relevant"] == "yes" and not (
                g["stance"] in WEAPON_STANCES or any(g[f] == "1" for f in WEAPON_FRAMES)):
            g["relevant"] = "no"  # v1.1: nuclear energy, plants and safety alone are out of scope
        gold[g["code_id"]] = g
sample = list(csv.DictReader(open(VAL / SAMPLE, encoding="utf-8")))
human = {}
for p in (CODES / "codes").glob("*.json"):
    d = json.load(open(p, encoding="utf-8"))
    d = d.get("data", d)
    if d.get("batch", "check") == BATCH:
        human[d["code_id"]] = d

rows = []
for s in sample:
    h = human.get(s["check_id"])
    if not h:
        continue
    g = gold[s["code_id"]]
    rec = {"check_id": s["check_id"], "code_id": s["code_id"], "voice": s["voice"], "era": s.get("era", s.get("year", "")),
           "adjudicated": g["adjudicated"], "human_relevant": h["relevant"], "model_relevant": g["relevant"],
           "human_stance": h.get("stance", ""), "model_stance": g["stance"]}
    framed = any(int(h.get(f, 0) or 0) for f in FR)
    for f in FR:
        rec[f"human_{f}"] = int(h.get(f, 0) or 0) if framed else ""
        rec[f"model_{f}"] = int(g[f])
    rows.append(rec)
print(f"{len(rows)} of {len(sample)} passages coded by the author")
if not rows:
    sys.exit()

out = []
def report(label, pairs):
    if not pairs:
        return
    agree = sum(a == b for a, b in pairs) / len(pairs)
    out.append({"field": label, "n": len(pairs), "pct_agree": round(100 * agree, 1),
                "alpha": round(alpha_nominal([list(p) for p in pairs]), 3)})

report("relevant", [(r["human_relevant"], r["model_relevant"]) for r in rows])
both = [r for r in rows if r["human_relevant"] == r["model_relevant"] == "yes"]
report("stance", [(r["human_stance"], r["model_stance"]) for r in both])
report("stance (consensus items)", [(r["human_stance"], r["model_stance"]) for r in both if r["adjudicated"] == "0"])
report("stance (adjudicated items)", [(r["human_stance"], r["model_stance"]) for r in both if r["adjudicated"] == "1"])
for f in FR:
    report(f, [(r[f"human_{f}"], r[f"model_{f}"]) for r in both if r[f"human_{f}"] != ""])

for name, recs in ((f"{PREFIX}_results.csv", rows), (f"{PREFIX}_agreement.csv", out)):
    with open(VAL / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
for o in out:
    print(o)
print("stance confusion (human -> model):",
      Counter((r["human_stance"], r["model_stance"]) for r in both if r["human_stance"] != r["model_stance"]).most_common(8))
