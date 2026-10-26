"""Validate the frame dictionaries against the coded validation sample (task A4).

Usage:
  python3 validate.py VALDIR OUTDIR merge     # merge coder files, agreement, disagreements to adjudicate
  python3 validate.py VALDIR OUTDIR score     # gold labels (consensus + adjudication) vs dictionaries

VALDIR holds sample.csv, codes_claude_a.csv, codes_claude_b.csv and, after adjudication,
adjudication.csv (code_id, field, value, reason). OUTDIR is the pipeline output folder
(passages.jsonl / turns.csv with dictionary counts).
"""
import csv, json, math, random, sys
from collections import Counter
from pathlib import Path

VAL, OUT, MODE = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
FIELDS = ["relevant"] + FR + ["stance"]


def alpha_nominal(units):
    """Krippendorff's alpha for nominal data. units: list of lists of values (one list per unit,
    one value per coder; None = missing). Units with fewer than two values are ignored."""
    pairs = Counter()
    for vals in units:
        vals = [v for v in vals if v is not None]
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


def _selftest():
    # Krippendorff (2011) nominal example: 4 coders, 12 units; alpha = 0.743
    data = [[1, 1, None, 1], [2, 2, 3, 2], [3, 3, 3, 3], [3, 3, 3, 3], [2, 2, 2, 2], [1, 2, 3, 4],
            [4, 4, 4, 4], [1, 1, 2, 1], [2, 2, 2, 2], [None, 5, 5, 5], [None, None, 1, 1], [None, None, 3, None]]
    a = alpha_nominal(data)
    assert abs(a - 0.743) < 0.001, a


def load_codes(name):
    return {r["code_id"]: r for r in csv.DictReader(open(VAL / name, encoding="utf-8"))}


def ci(units, n=1000, seed=20261026):
    rnd = random.Random(seed); v = []
    for _ in range(n):
        s = [rnd.choice(units) for _ in units]
        a = alpha_nominal(s)
        if not math.isnan(a):
            v.append(a)
    v.sort()
    return v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]


def merge():
    _selftest()
    A, B = load_codes("codes_claude_a.csv"), load_codes("codes_claude_b.csv")
    sample = {r["code_id"]: r for r in csv.DictReader(open(VAL / "sample.csv", encoding="utf-8"))}
    assert set(A) == set(B) == set(sample), "coder files must cover the whole sample"
    ids = sorted(sample)
    rows = []
    for f in FIELDS:
        # frames and stance are only defined when both coders said relevant=yes
        use = ids if f == "relevant" else [i for i in ids if A[i]["relevant"] == B[i]["relevant"] == "yes"]
        units = [[A[i][f], B[i][f]] for i in use]
        a = alpha_nominal(units); lo, hi = ci(units)
        agree = sum(x == y for x, y in units)
        rows.append({"field": f, "units": len(use), "pct_agree": round(100 * agree / len(use), 1),
                     "alpha": round(a, 3), "alpha_lo": round(lo, 3), "alpha_hi": round(hi, 3),
                     "positives_a": sum(x == "1" for x, _ in units) if f in FR else "",
                     "positives_b": sum(y == "1" for _, y in units) if f in FR else ""})
    with open(VAL / "agreement.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)
    # disagreements to adjudicate (frames/stance only where both said relevant=yes)
    dis = []
    for i in ids:
        a, b = A[i], B[i]
        diff = ["relevant"] if a["relevant"] != b["relevant"] else []
        if a["relevant"] == b["relevant"] == "yes":
            diff += [f for f in FR + ["stance"] if a[f] != b[f]]
        if diff:
            dis.append({"code_id": i, "fields": ";".join(diff), "voice": sample[i]["voice"],
                        "text": sample[i]["text"],
                        "a": json.dumps({f: a[f] for f in FIELDS} | {"note": a["note"]}),
                        "b": json.dumps({f: b[f] for f in FIELDS} | {"note": b["note"]})})
    with open(VAL / "disagreements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dis[0]) if dis else ["code_id"]); w.writeheader(); w.writerows(dis)
    print(f"{len(dis)} passages with at least one disagreement -> disagreements.csv")


def gold():
    A, B = load_codes("codes_claude_a.csv"), load_codes("codes_claude_b.csv")
    adj = {}
    if (VAL / "adjudication.csv").exists():
        for r in csv.DictReader(open(VAL / "adjudication.csv", encoding="utf-8")):
            adj[(r["code_id"], r["field"])] = r["value"]
    out = {}
    for i in A:
        g, flag = {}, 0
        for f in FIELDS:
            if (i, f) in adj:
                g[f] = adj[(i, f)]; flag = 1
            elif A[i][f] == B[i][f]:
                g[f] = A[i][f]
            else:
                g[f] = None  # unresolved
        if g["relevant"] == "no":
            g.update({f: "0" for f in FR}); g["stance"] = ""
        g["adjudicated"] = flag
        out[i] = g
    return out


def score():
    G = gold()
    unresolved = [i for i, g in G.items() if any(g[f] is None for f in FIELDS)]
    assert not unresolved, f"{len(unresolved)} passages still unresolved, e.g. {unresolved[:5]}"
    sample = {r["code_id"]: r for r in csv.DictReader(open(VAL / "sample.csv", encoding="utf-8"))}
    dic = {}
    for line in open(OUT / "passages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        dic[r["pid"]] = r
    with open(VAL / "gold.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["code_id", "voice", "era"] + FIELDS + ["adjudicated"])
        for i in sorted(G):
            w.writerow([i, sample[i]["voice"], sample[i]["era"]] + [G[i][f] for f in FIELDS] + [G[i]["adjudicated"]])
    # dictionary performance on relevant, nuclear (non near-miss) passages
    perf = []
    rel = [i for i in G if G[i]["relevant"] == "yes" and sample[i]["voice"] != "near_miss"]
    for f in FR:
        tp = fp = fn = tn = 0
        for i in rel:
            d = int(dic[sample[i]["pid"]][f]) > 0
            g = G[i][f] == "1"
            tp += d and g; fp += d and not g; fn += g and not d; tn += not d and not g
        p = tp / (tp + fp) if tp + fp else float("nan"); r = tp / (tp + fn) if tp + fn else float("nan")
        f1 = 2 * p * r / (p + r) if p + r else 0
        perf.append({"frame": f, "gold_positive": tp + fn, "dict_positive": tp + fp, "tp": tp, "fp": fp,
                     "fn": fn, "tn": tn, "precision": round(p, 3), "recall": round(r, 3), "f1": round(f1, 3)})
    with open(VAL / "dictionary_performance.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(perf[0])); w.writeheader(); w.writerows(perf)
    for r in perf:
        print(r)
    # keyword-filter precision: share of sampled nuclear passages that are relevant
    nuc = [i for i in G if sample[i]["voice"] != "near_miss"]
    nm = [i for i in G if sample[i]["voice"] == "near_miss"]
    print("relevance of keyword-selected passages:", sum(G[i]["relevant"] == "yes" for i in nuc), "/", len(nuc))
    print("near-miss passages that are relevant (missed by filter):", sum(G[i]["relevant"] == "yes" for i in nm), "/", len(nm))
    print("stance distribution:", Counter(G[i]["stance"] for i in rel))


if __name__ == "__main__":
    {"merge": merge, "score": score}[MODE]()
