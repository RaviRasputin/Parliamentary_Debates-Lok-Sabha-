"""Indo-US nuclear deal extension (task E3): merge the two blind Claude coders' codes of the
2000-08 sample, build gold codes after Opus adjudication, and compute the 2000-08 series.

Usage:
  python3 -I e3.py VALDIR merge CODERDIR   # CODERDIR/iso_a*/codes.csv, iso_b*/codes.csv -> codes3_claude_a/b.csv,
                                           # agreement3.csv, disagreements3.csv
  python3 -I e3.py VALDIR gold             # + adjudication3.csv (code_id, field, value, reason) -> gold3.csv
  python3 -I e3.py VALDIR series           # gold3.csv + sample3.csv -> e3_gap.csv, e3_stance.csv, e3_deal.csv, e3_frames.csv
"""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

VAL, MODE = Path(sys.argv[1]), sys.argv[2]
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
FIELDS = ["relevant"] + FR + ["stance", "deal_stance"]
COLS = ["code_id", "coder", "relevant"] + FR + ["stance", "deal_stance", "confidence", "note"]
POS = ["pro_bomb", "keep_option", "disarmament", "critical_of_tests", "peaceful_only"]
DEAL = ["support", "oppose", "conditional"]
WEAPON_STANCES = {"pro_bomb", "keep_option", "disarmament", "critical_of_tests"}
WEAPON_FRAMES = ["disarmament", "option_open", "discrimination", "deterrence_weapon", "security_threat"]
PERIODS = ["2000-04", "2004-05", "2005-08", "2008"]
GROUPS = ["LS_left", "LS_bjp", "LS_congress", "LS_other", "RS_member"]


def alpha_nominal(units):
    """Krippendorff's alpha, nominal (same as validate.py)."""
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


def clean(r):
    """Normalise one coder row; refuse a row with extra fields (a shifted row)."""
    assert r.get(None) in (None, [], [""]) or not any(x.strip() for x in r[None]), f"extra fields in {r['code_id']}"
    r = {k: (v or "").strip() for k, v in r.items() if k is not None}
    if r.get("relevant") == "no":
        r.update({f: "0" for f in FR}); r["stance"] = r["deal_stance"] = ""
    return r


def merge():
    coder_dir = Path(sys.argv[3])
    sample = {r["code_id"]: r for r in csv.DictReader(open(VAL / "sample3_blind.csv", encoding="utf-8"))}
    codes = {}
    for c in "ab":
        rows = {}
        for p in sorted(coder_dir.glob(f"iso_{c}*/codes.csv")):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                r = clean(r)
                rows[r["code_id"]] = r
        missing = set(sample) - set(rows)
        assert not missing, f"coder {c} missing {len(missing)} passages, e.g. {sorted(missing)[:5]}"
        with open(VAL / f"codes3_claude_{c}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore"); w.writeheader()
            w.writerows(rows[i] for i in sorted(sample))
        codes[c] = rows
    A, B = codes["a"], codes["b"]
    ids = sorted(sample)
    agree = []
    for f in FIELDS:
        use = ids if f == "relevant" else [i for i in ids if A[i]["relevant"] == B[i]["relevant"] == "yes"]
        units = [[A[i][f], B[i][f]] for i in use]
        agree.append({"field": f, "units": len(use), "pct_agree": round(100 * sum(x == y for x, y in units) / len(use), 1),
                      "alpha": round(alpha_nominal(units), 3)})
    with open(VAL / "agreement3.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(agree[0])); w.writeheader(); w.writerows(agree)
    for a in agree:
        print(a)
    dis = []
    for i in ids:
        a, b = A[i], B[i]
        diff = ["relevant"] if a["relevant"] != b["relevant"] else []
        if a["relevant"] == b["relevant"] == "yes":
            diff += [f for f in FR + ["stance", "deal_stance"] if a[f] != b[f]]
        if diff:
            dis.append({"code_id": i, "fields": ";".join(diff), "text": sample[i]["text"],
                        "a": json.dumps({f: a[f] for f in FIELDS} | {"note": a["note"]}),
                        "b": json.dumps({f: b[f] for f in FIELDS} | {"note": b["note"]})})
    with open(VAL / "disagreements3.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["code_id", "fields", "text", "a", "b"]); w.writeheader(); w.writerows(dis)
    print(len(dis), "passages with a disagreement -> disagreements3.csv")


def gold():
    A = {r["code_id"]: r for r in csv.DictReader(open(VAL / "codes3_claude_a.csv", encoding="utf-8"))}
    B = {r["code_id"]: r for r in csv.DictReader(open(VAL / "codes3_claude_b.csv", encoding="utf-8"))}
    adj = {}
    if (VAL / "adjudication3.csv").exists():
        for r in csv.DictReader(open(VAL / "adjudication3.csv", encoding="utf-8")):
            adj[(r["code_id"], r["field"])] = r["value"].strip()
    out, unresolved = [], []
    for i in sorted(A):
        g, flag = {"code_id": i}, 0
        for f in FIELDS:
            if (i, f) in adj:
                g[f] = adj[(i, f)]; flag = 1
            elif A[i][f] == B[i][f]:
                g[f] = A[i][f]
            else:
                g[f] = None
        if g["relevant"] == "no":
            g.update({f: "0" for f in FR}); g["stance"] = g["deal_stance"] = ""
        if any(g[f] is None for f in FIELDS):
            unresolved.append(i)
        g["adjudicated"] = flag
        out.append(g)
    assert not unresolved, f"{len(unresolved)} unresolved, e.g. {unresolved[:5]}"
    with open(VAL / "gold3.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["code_id"] + FIELDS + ["adjudicated"]); w.writeheader(); w.writerows(out)
    print(len(out), "gold rows;", sum(g["adjudicated"] for g in out), "adjudicated")


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    kl = lambda x, y: sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def fdist(rs):
    c = Counter()
    for r in rs:
        for f in FR:
            c[f] += r[f] == "1"
    t = sum(c.values())
    return [c[f] / t if t else 0 for f in FR], t


def cdist(rs, key, cats):
    c = Counter(r[key] for r in rs if r[key] in cats)
    t = sum(c.values())
    return [c[k] / t if t else 0 for k in cats], t


def gap(a, b, kind, n=1000, seed=20261026):
    f = {"frames": fdist, "stance": lambda rs: cdist(rs, "stance", POS),
         "deal": lambda rs: cdist(rs, "deal_stance", DEAL)}[kind]
    (p, tp), (q, tq) = f(a), f(b)
    if not (tp and tq):
        return "", "", ""
    point = jsd(p, q)
    rnd = random.Random(seed); v = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]; sb = [rnd.choice(b) for _ in b]
        (p, tp), (q, tq) = f(sa), f(sb)
        if tp and tq:
            v.append(jsd(p, q))
    v.sort()
    return round(point, 3), round(v[int(.05 * len(v))], 3), round(v[int(.95 * len(v)) - 1], 3)


def series():
    meta = {r["code_id"]: r for r in csv.DictReader(open(VAL / "sample3.csv", encoding="utf-8"))}
    rel = []
    for g in csv.DictReader(open(VAL / "gold3.csv", encoding="utf-8")):
        # weapons and security (codebook 1.1) or about the deal (1.2)
        keep = g["relevant"] == "yes" and (g["stance"] in WEAPON_STANCES or any(g[f] == "1" for f in WEAPON_FRAMES)
                                          or g["deal_stance"] not in ("", "none"))
        if keep:
            g.update(voice=meta[g["code_id"]]["voice"], period=meta[g["code_id"]]["era"])
            rel.append(g)
    print(len(rel), "relevant passages")
    cell = defaultdict(list)
    for r in rel:
        cell[(r["voice"], r["period"])].append(r)
    gaps = []
    for p in PERIODS:
        mins = cell[("minister", p)]
        for gname in GROUPS:
            grp = cell[(gname, p)]
            rec = {"period": p, "group": gname, "n_ministers": len(mins), "n_group": len(grp)}
            for kind in ("frames", "stance", "deal"):
                rec[kind], rec[kind + "_lo"], rec[kind + "_hi"] = gap(mins, grp, kind) if len(grp) >= 10 else ("", "", "")
            gaps.append(rec)
    out = {"e3_gap.csv": gaps, "e3_stance.csv": [], "e3_deal.csv": [], "e3_frames.csv": []}
    for (v, p), rs in sorted(cell.items(), key=lambda kv: (kv[0][0], PERIODS.index(kv[0][1]))):
        s, d = Counter(r["stance"] for r in rs), Counter(r["deal_stance"] for r in rs)
        out["e3_stance.csv"].append({"voice": v, "period": p, "n": len(rs), **{k: s[k] for k in POS + ["other_country", "neutral"]}})
        out["e3_deal.csv"].append({"voice": v, "period": p, "n": len(rs), **{k: d[k] for k in DEAL + ["neutral", "none"]}})
        fd, t = fdist(rs)
        out["e3_frames.csv"].append({"voice": v, "period": p, "n": len(rs), "frame_uses": t, **{f: round(x, 3) for f, x in zip(FR, fd)}})
    for name, recs in out.items():
        with open(VAL / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
        print("==", name)
        for r in recs:
            print(r)


if __name__ == "__main__":
    {"merge": merge, "gold": gold, "series": series}[MODE]()
