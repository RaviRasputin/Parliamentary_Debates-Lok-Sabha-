"""Re-measure the executive-legislative gap on the validation sample with the adjudicated
codes, beside the dictionary codes for the same passages (robustness for the paper)."""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

VAL, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
ERAS = ["1962-68", "1969-79", "1980-89", "1990-97", "1998-99"]
gold = {r["code_id"]: r for r in csv.DictReader(open(VAL / "gold.csv", encoding="utf-8"))}
sample = {r["code_id"]: r for r in csv.DictReader(open(VAL / "sample.csv", encoding="utf-8"))}
dic = {}
for line in open(OUT / "passages.jsonl", encoding="utf-8"):
    r = json.loads(line); dic[r["pid"]] = r

def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    kl = lambda x, y: sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

def dist(ids, src):
    c = Counter()
    for i in ids:
        for f in FR:
            c[f] += (gold[i][f] == "1") if src == "gold" else min(1, int(dic[sample[i]["pid"]][f]))
    t = sum(c.values())
    return [c[f] / t if t else 0 for f in FR], t

def boot(a, b, src, n=500, seed=1):
    rnd = random.Random(seed); v = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]; sb = [rnd.choice(b) for _ in b]
        (p, tp), (q, tq) = dist(sa, src), dist(sb, src)
        if tp and tq: v.append(jsd(p, q))
    v.sort(); return v[int(.05 * len(v))], v[int(.95 * len(v)) - 1]

rows = []
for e in ERAS:
    rel = [i for i in gold if gold[i]["relevant"] == "yes" and sample[i]["era"] == e]
    mem = [i for i in rel if sample[i]["voice"] in ("LS_member", "RS_member")]
    mea = [i for i in rel if sample[i]["voice"] == "MEA"]
    mins = [i for i in rel if sample[i]["voice"] == "minister"]
    rec = {"era": e, "members": len(mem), "mea": len(mea), "ministers": len(mins)}
    for src in ("gold", "dict"):
        rec[f"{src}_mea_mem"] = round(jsd(dist(mea, src)[0], dist(mem, src)[0]), 3)
        lo, hi = boot(mea, mem, src); rec[f"{src}_mea_mem_lo"], rec[f"{src}_mea_mem_hi"] = round(lo, 3), round(hi, 3)
        rec[f"{src}_min_mem"] = round(jsd(dist(mins, src)[0], dist(mem, src)[0]), 3)
    rows.append(rec)
with open(VAL / "gap_validation.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)

# stance shares by voice x era (gold)
st = defaultdict(Counter)
for i, g in gold.items():
    if g["relevant"] == "yes" and sample[i]["voice"] != "near_miss":
        v = "members" if sample[i]["voice"] in ("LS_member", "RS_member") else sample[i]["voice"]
        st[(v, sample[i]["era"])][g["stance"]] += 1
out = []
for (v, e), c in sorted(st.items()):
    n = sum(c.values())
    out.append({"voice": v, "era": e, "n": n, **{k: c[k] for k in ["pro_bomb", "keep_option", "disarmament", "critical_of_tests", "peaceful_only", "other_country", "neutral"]}})
with open(VAL / "stance_by_voice_era.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out: print(r)
