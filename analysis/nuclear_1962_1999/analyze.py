"""Aggregate turns.csv into yearly salience, frame shares and executive-legislative distance."""
import csv, json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(sys.argv[1])
FR = ["disarmament", "peaceful_use", "option_open", "discrimination", "deterrence_weapon", "security_threat", "autonomy"]
rows = list(csv.DictReader(open(OUT / "turns.csv", encoding="utf-8")))
for r in rows:
    r["year"] = int(r["year"])
    for k in r:
        if k in FR or k == "consensus" or k.startswith("ph_") or k in ("nuc_hits", "words"):
            r[k] = int(r[k])


def voice(r):
    if r["house"] in ("LS", "RS"):
        return "ministers" if r["role"] == "executive" else "members"
    return r["house"]  # MEA


PERIODS = [(1962, 1963), (1964, 1968), (1969, 1973), (1974, 1974), (1975, 1979), (1980, 1984), (1985, 1989),
           (1990, 1993), (1994, 1997), (1998, 1998), (1999, 1999)]
plab = lambda a, b: str(a) if a == b else f"{a}–{str(b)[2:]}"


def dist(rs):
    c = Counter()
    for r in rs:
        for f in FR:
            c[f] += r[f]
    tot = sum(c.values())
    return [c[f] / tot if tot else 0 for f in FR], tot


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    kl = lambda x, y: sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def jsd_ci(a, b, n=300, seed=1):
    rnd = random.Random(seed); vals = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]; sb = [rnd.choice(b) for _ in b]
        (p, tp), (q, tq) = dist(sa), dist(sb)
        if tp and tq:
            vals.append(jsd(p, q))
    vals.sort()
    return vals[int(.05 * len(vals))], vals[int(.95 * len(vals)) - 1]


by = defaultdict(list)
for r in rows:
    by[(voice(r), r["year"])].append(r)

# 1. salience per year per house (nuclear turns, keyword hits per million words)
sizes = {(s["source"], int(s["year"])): int(s["words"]) for s in csv.DictReader(open(OUT / "corpus_sizes.csv"))}
sal = []
for y in range(1962, 2000):
    rec = {"year": y}
    for h in ("LS", "RS", "MEA"):
        hs = [r for r in rows if r["house"] == h and r["year"] == y]
        rec[f"{h}_turns"] = len(hs)
        w = sizes.get((h, y), 0)
        rec[f"{h}_per_m"] = round(sum(r["nuc_hits"] for r in hs) / w * 1e6, 1) if w else ""
    rec["min_turns"] = len(by[("ministers", y)]); rec["mem_turns"] = len(by[("members", y)])
    sal.append(rec)

# 2. period frame shares + distances
per = []
for a, b in PERIODS:
    g = lambda v: [r for y in range(a, b + 1) for r in by[(v, y)]]
    mn, mm, mea = g("ministers"), g("members"), g("MEA")
    (pm, tm), (pn, tn), (pe, te) = dist(mn), dist(mm), dist(mea)
    rec = {"period": plab(a, b), "ministers_turns": len(mn), "members_turns": len(mm), "mea_chunks": len(mea)}
    for name, p in (("min", pm), ("mem", pn), ("mea", pe)):
        for f, v in zip(FR, p):
            rec[f"{name}_{f}"] = round(v, 3)
    rec["jsd_min_mem"] = round(jsd(pm, pn), 4)
    lo, hi = jsd_ci(mn, mm); rec["jsd_min_mem_lo"], rec["jsd_min_mem_hi"] = round(lo, 4), round(hi, 4)
    rec["jsd_mea_mem"] = round(jsd(pe, pn), 4) if te else ""
    if te:
        lo, hi = jsd_ci(mea, mm); rec["jsd_mea_mem_lo"], rec["jsd_mea_mem_hi"] = round(lo, 4), round(hi, 4)
    rec["consensus_per100_mem"] = round(100 * sum(r["consensus"] for r in mm) / len(mm), 2) if mm else ""
    rec["consensus_per100_min"] = round(100 * sum(r["consensus"] for r in mn) / len(mn), 2) if mn else ""
    per.append(rec)

# 3. lead-lag: first year with >=2 uses per voice
phr = [k[3:] for k in rows[0] if k.startswith("ph_")]
lead = []
for p in phr:
    rec = {"phrase": p}
    for v in ("members", "ministers", "MEA"):
        yrs = [y for y in range(1962, 2000) if sum(r["ph_" + p] for r in by[(v, y)]) >= 2]
        rec[v] = yrs[0] if yrs else ""
        rec[v + "_total"] = sum(r["ph_" + p] for y in range(1962, 2000) for r in by[(v, y)])
    lead.append(rec)

# 4. phrase counts per year per voice (for charts)
ph_year = []
for y in range(1962, 2000):
    for v in ("members", "ministers", "MEA"):
        rec = {"year": y, "voice": v, "turns": len(by[(v, y)])}
        for p in phr:
            rec[p] = sum(r["ph_" + p] for r in by[(v, y)])
        ph_year.append(rec)

# 5. most active members on nuclear issues by period
active = []
for a, b in PERIODS:
    c = Counter(r["speaker"].split("(")[0].strip().upper() for y in range(a, b + 1) for r in by[("members", y)])
    active.append({"period": plab(a, b), "top": "; ".join(f"{n} ({k})" for n, k in c.most_common(8))})

def dump(name, recs):
    with open(OUT / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)

dump("salience_by_year.csv", sal); dump("frames_by_period.csv", per); dump("lead_lag.csv", lead)
dump("phrases_by_year.csv", ph_year); dump("active_members.csv", active)
for r in per:
    print(r["period"], r["ministers_turns"], r["members_turns"], r["mea_chunks"], r["jsd_min_mem"],
          (r["jsd_min_mem_lo"], r["jsd_min_mem_hi"]), r["jsd_mea_mem"])
