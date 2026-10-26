"""Government vs opposition, party families, and robustness checks for the gap measure."""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(sys.argv[1])
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
rows = list(csv.DictReader(open(OUT / "turns_party.csv", encoding="utf-8")))
for r in rows:
    r["year"] = int(r["year"])
    for k in list(r):
        if k in FR or k == "consensus" or k.startswith("ph_"):
            r[k] = int(r[k])

PERIODS = [(1962, 1968), (1969, 1973), (1974, 1974), (1975, 1979), (1980, 1989), (1990, 1993), (1994, 1997), (1998, 1999)]
plab = lambda a, b: str(a) if a == b else f"{a}–{str(b)[2:]}"


def dist(rs, frames=FR):
    c = Counter()
    for r in rs:
        for f in frames:
            c[f] += r[f]
    t = sum(c.values())
    return [c[f] / t if t else 0 for f in frames], t


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    kl = lambda x, y: sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def ci(a, b, frames=FR, n=300, seed=7):
    rnd = random.Random(seed); v = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]; sb = [rnd.choice(b) for _ in b]
        (p, tp), (q, tq) = dist(sa, frames), dist(sb, frames)
        if tp and tq:
            v.append(jsd(p, q))
    v.sort()
    return round(v[int(.05 * len(v))], 4), round(v[int(.95 * len(v)) - 1], 4)


def sel(a, b, **kw):
    out = []
    for r in rows:
        if not a <= r["year"] <= b:
            continue
        if all((r[k] in v) if isinstance(v, (set, tuple)) else r[k] == v for k, v in kw.items()):
            out.append(r)
    return out


parl = {"LS", "RS"}
PH = {"LS"}  # party labels are reliable only for the Lok Sabha (matched to election winners)
# 1. side-level gaps vs the executive (MEA and ministers)
side_rows = []
for a, b in PERIODS:
    mea = sel(a, b, house="MEA"); mins = sel(a, b, house=parl, role="executive")
    for s in ("government", "opposition", "outside support"):
        mem = sel(a, b, house=PH, role="member", side=s)
        if len(mem) < 30:
            continue
        p, _ = dist(mem)
        rec = {"period": plab(a, b), "side": s, "turns": len(mem),
               "jsd_vs_mea": round(jsd(p, dist(mea)[0]), 4), "jsd_vs_ministers": round(jsd(p, dist(mins)[0]), 4)}
        rec["mea_lo"], rec["mea_hi"] = ci(mem, mea)
        rec["consensus_per100"] = round(100 * sum(r["consensus"] for r in mem) / len(mem), 2)
        for f, v in zip(FR, p):
            rec[f] = round(v, 3)
        side_rows.append(rec)

# 2. party families: frame shares and phrase rates by era
ERAS = [(1962, 1973), (1974, 1979), (1980, 1989), (1990, 1997), (1998, 1999)]
FAMS = ["Congress", "Jana Sangh / BJP", "Left", "Socialist / Janata", "Swatantra"]
fam_rows = []
for a, b in ERAS:
    for f in FAMS:
        mem = sel(a, b, house=PH, role="member", family=f)
        if len(mem) < 25:
            continue
        p, _ = dist(mem)
        rec = {"era": plab(a, b), "family": f, "turns": len(mem)}
        for k, v in zip(FR, p):
            rec[k] = round(v, 3)
        for ph in ("keep option open", "nuclear option", "discriminatory treaty", "nuclear apartheid", "weaponisation"):
            rec["per100_" + ph] = round(100 * sum(r["ph_" + ph] for r in mem) / len(mem), 2)
        rec["consensus_per100"] = round(100 * sum(r["consensus"] for r in mem) / len(mem), 2)
        fam_rows.append(rec)

# 3. first use of key phrases by side and family
phr = [k[3:] for k in rows[0] if k.startswith("ph_")]
lead = []
for p in phr:
    rec = {"phrase": p}
    for label, kw in [("opposition", {"side": "opposition"}), ("government benches", {"side": "government"}),
                      ("Jana Sangh / BJP", {"family": "Jana Sangh / BJP"}), ("Left", {"family": "Left"}),
                      ("Socialist / Janata", {"family": "Socialist / Janata"}), ("Congress", {"family": "Congress"})]:
        yrs = sorted({r["year"] for r in sel(1962, 1999, house=PH, role="member", **kw) if r["ph_" + p] > 0})
        rec[label] = yrs[0] if yrs else ""
    lead.append(rec)

# 4. robustness: main MEA-members gap (a) without the security frame, (b) LS only, (c) RS only
FR6 = [f for f in FR if f != "security_threat"]
rob = []
for a, b in PERIODS:
    mea = sel(a, b, house="MEA")
    rec = {"period": plab(a, b)}
    for label, frames, houses in [("all7", FR, parl), ("no_security", FR6, parl), ("LS_only", FR, {"LS"}), ("RS_only", FR, {"RS"})]:
        mem = sel(a, b, house=houses, role="member")
        rec[label] = round(jsd(dist(mem, frames)[0], dist(mea, frames)[0]), 4)
    lo, hi = ci(sel(a, b, house=parl, role="member"), mea, FR6)
    rec["no_security_lo"], rec["no_security_hi"] = lo, hi
    rob.append(rec)

# coverage
cov = []
for a, b in PERIODS:
    m = sel(a, b, house=PH, role="member")
    c = Counter(r["side"] or "unmatched" for r in m)
    cov.append({"period": plab(a, b), "member_turns": len(m), **{k: c[k] for k in
               ("government", "opposition", "outside support", "unknown", "unclassified period", "unmatched")}})


def dump(name, recs):
    with open(OUT / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)


for n, rr in [("gap_by_side.csv", side_rows), ("frames_by_family.csv", fam_rows), ("lead_lag_party.csv", lead),
              ("robustness.csv", rob), ("party_coverage.csv", cov)]:
    dump(n, rr)
    print("==", n)
    for r in rr:
        print(" | ".join(str(v) for v in r.values()))
