"""Rebuild the executive-legislative gap series on Claude-coded, Opus-adjudicated passages
(validation/gold.csv + gold2.csv), 1962-99, six eras. Outputs to validation/series_*.csv."""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

VAL, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
POS = ["pro_bomb", "keep_option", "disarmament", "critical_of_tests", "peaceful_only"]
STANCES = POS + ["other_country", "neutral"]
ERAS = [("1962-68", 1962, 1968), ("1969-79", 1969, 1979), ("1980-89", 1980, 1989),
        ("1990-93", 1990, 1993), ("1994-97", 1994, 1997), ("1998-99", 1998, 1999)]
era_of = lambda y: next(e for e, a, b in ERAS if a <= y <= b)

meta = {}
for name in ("sample.csv", "sample2.csv"):
    for r in csv.DictReader(open(VAL / name, encoding="utf-8")):
        meta[r["code_id"]] = r
rows = []
for name in ("gold.csv", "gold2.csv"):
    for g in csv.DictReader(open(VAL / name, encoding="utf-8")):
        m = meta[g["code_id"]]
        if m["voice"] == "near_miss":
            continue
        g.update({"year": int(m["year"]), "era": era_of(int(m["year"])), "voice": m["voice"],
                  "side": m.get("side", ""), "party": m.get("party", ""), "pid": m["pid"]})
        g["group"] = "members" if g["voice"] in ("LS_member", "RS_member") else g["voice"]
        rows.append(g)
rel = [r for r in rows if r["relevant"] == "yes"]
print("coded", len(rows), "relevant", len(rel))


def fdist(rs):
    c = Counter()
    for r in rs:
        for f in FR:
            c[f] += r[f] == "1"
    t = sum(c.values())
    return [c[f] / t if t else 0 for f in FR], t


def sdist(rs, cats):
    c = Counter(r["stance"] for r in rs if r["stance"] in cats)
    t = sum(c.values())
    return [c[k] / t if t else 0 for k in cats], t


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    kl = lambda x, y: sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def gap(a, b, kind, n=1000, seed=20261026):
    f = (lambda rs: fdist(rs)) if kind == "frames" else (lambda rs: sdist(rs, POS))
    (p, tp), (q, tq) = f(a), f(b)
    point = jsd(p, q) if tp and tq else float("nan")
    rnd = random.Random(seed); v = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]; sb = [rnd.choice(b) for _ in b]
        (p, tp), (q, tq) = f(sa), f(sb)
        if tp and tq:
            v.append(jsd(p, q))
    v.sort()
    return round(point, 3), round(v[int(.05 * len(v))], 3), round(v[int(.95 * len(v)) - 1], 3)


cell = defaultdict(list)
for r in rel:
    cell[(r["group"], r["era"])].append(r)
series = []
for e, _, _ in ERAS:
    mea, mem, mins = cell[("MEA", e)], cell[("members", e)], cell[("minister", e)]
    rec = {"era": e, "n_mea": len(mea), "n_members": len(mem), "n_ministers": len(mins)}
    for kind in ("frames", "stance"):
        for lab, a, b in (("mea_mem", mea, mem), ("min_mem", mins, mem), ("mea_min", mea, mins)):
            pt, lo, hi = gap(a, b, kind)
            rec[f"{kind}_{lab}"], rec[f"{kind}_{lab}_lo"], rec[f"{kind}_{lab}_hi"] = pt, lo, hi
    series.append(rec)

stance = []
for (g, e), rs in sorted(cell.items()):
    c = Counter(r["stance"] for r in rs)
    stance.append({"group": g, "era": e, "n": len(rs), **{k: c[k] for k in STANCES},
                   **{f"share_{k}": round(c[k] / len(rs), 3) for k in STANCES}})
frames = []
for (g, e), rs in sorted(cell.items()):
    p, t = fdist(rs)
    frames.append({"group": g, "era": e, "n": len(rs), **{f: round(x, 3) for f, x in zip(FR, p)},
                   **{f"pct_passages_{f}": round(sum(r[f] == "1" for r in rs) / len(rs), 3) for f in FR}})

# Lok Sabha members by side vs the MEA (sides assigned 1962-04-16 to 2004-05-16 only)
sides = []
for e, _, _ in ERAS:
    mea = cell[("MEA", e)]
    for s in ("government", "opposition"):
        mem = [r for r in cell[("members", e)] if r["voice"] == "LS_member" and r["side"] == s]
        if len(mem) < 15:
            continue
        rec = {"era": e, "side": s, "n": len(mem)}
        for kind in ("frames", "stance"):
            pt, lo, hi = gap(mea, mem, kind)
            rec[f"{kind}_vs_mea"], rec[f"{kind}_lo"], rec[f"{kind}_hi"] = pt, lo, hi
        c = Counter(r["stance"] for r in mem)
        rec.update({k: c[k] for k in POS})
        sides.append(rec)

# dictionary vs validated codes on all relevant coded passages
dic = {}
for line in open(OUT / "passages.jsonl", encoding="utf-8"):
    r = json.loads(line); dic[r["pid"]] = r
perf = []
for f in FR:
    tp = fp = fn = 0
    for r in rel:
        d = int(dic[r["pid"]][f]) > 0; g = r[f] == "1"
        tp += d and g; fp += d and not g; fn += g and not d
    p = tp / (tp + fp) if tp + fp else 0; rc = tp / (tp + fn) if tp + fn else 0
    perf.append({"frame": f, "gold_pos": tp + fn, "precision": round(p, 3), "recall": round(rc, 3),
                 "f1": round(2 * p * rc / (p + rc), 3) if p + rc else 0})

def dump(name, recs):
    with open(VAL / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
for n, recs in (("series_gap.csv", series), ("series_stance.csv", stance), ("series_frames.csv", frames),
                ("series_sides.csv", sides), ("dictionary_performance_full.csv", perf)):
    dump(n, recs)
    print("==", n)
    for r in recs:
        print({k: v for k, v in r.items() if not k.startswith("share_") and not k.startswith("pct_")})
