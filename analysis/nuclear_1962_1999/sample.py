"""Draw the validation sample (task A1): 500 coded-window passages stratified by voice x era,
plus 50 near-miss passages (no nuclear keyword, but atom/bomb/Pokhran/reactor/test+China words)
to estimate the keyword filter's recall.

Usage: python3 -I sample.py OUTDIR VALIDATION_DIR
  OUTDIR must hold passages.jsonl, turns_party.csv and near_miss.jsonl (from extract.py / party.py).
"""
import csv, json, random, re, sys
from collections import defaultdict
from pathlib import Path

OUT, VAL = Path(sys.argv[1]), Path(sys.argv[2])
SEED = 20261026
PER_CELL, NEAR_PER_ERA, MIN_WORDS, CAP_WORDS = 25, 10, 25, 250
ERAS = [("1962-68", 1962, 1968), ("1969-79", 1969, 1979), ("1980-89", 1980, 1989),
        ("1990-97", 1990, 1997), ("1998-99", 1998, 1999)]
VOICES = ["LS_member", "RS_member", "minister", "MEA"]

# copy of NUC in extract.py (keep in sync); used only to centre the 250-word cap
NUC = re.compile(r"\bnuclear\b|\batomic\b|\batom bombs?\b|\bNPT\b|\bCTBT\b|non-?\s?proliferation|"
                 r"pokh?a?ran|test[- ]ban|plutonium|fissile|परमाणु|आणविक|न्यूक्लियर|"
                 r"123 agreement|hyde act|civil nuclear|\bNSG\b|nuclear suppliers group|separation plan|IAEA", re.I)


def era_of(year):
    return next((e for e, a, b in ERAS if a <= year <= b), None)


def voice_of(r):
    if r["house"] == "MEA":
        return "MEA"
    if r["house"] == "LS" and r["role"] == "member":
        return "LS_member"
    if r["house"] == "RS" and r["role"] == "member":
        return "RS_member"
    if r["house"] in ("LS", "RS") and r["role"] == "executive":
        return "minister"
    return None


def cap(text):
    words = text.split()
    if len(words) <= CAP_WORDS:
        return text
    hit = next((i for i, w in enumerate(words) if NUC.search(w)), None)
    if hit is None:
        m = NUC.search(text)
        hit = len(text[:m.start()].split()) if m else 0
    start = max(0, min(hit - CAP_WORDS // 2, len(words) - CAP_WORDS))
    return " ".join(words[start:start + CAP_WORDS])


def draw(pools, per_cell, rnd, label):
    """pools: era -> list of eligible rows (sorted). Take per_cell from each era; a short cell
    takes all it has and is topped up from the nearest eras (remaining rows), printing the shortfall."""
    names = [e for e, _, _ in ERAS]
    chosen = {e: [] for e in names}
    rest = {}
    for e in names:
        pool = pools.get(e, [])
        pick = rnd.sample(pool, min(per_cell, len(pool)))
        chosen[e] = pick
        ids = {id(x) for x in pick}
        rest[e] = [x for x in pool if id(x) not in ids]
    for i, e in enumerate(names):
        need = per_cell - len(chosen[e])
        if need <= 0:
            continue
        print(f"SHORTFALL {label} {e}: {len(chosen[e])} eligible, need {need} more", flush=True)
        for dist in range(1, len(names)):
            if need <= 0:
                break
            for j in (i - dist, i + dist):
                if need <= 0 or not 0 <= j < len(names):
                    continue
                take = rnd.sample(rest[names[j]], min(need, len(rest[names[j]])))
                ids = {id(x) for x in take}
                rest[names[j]] = [x for x in rest[names[j]] if id(x) not in ids]
                chosen[e] += take
                need -= len(take)
                print(f"  topped up {len(take)} from {names[j]}", flush=True)
        if need > 0:
            print(f"  STILL SHORT by {need} for {label} {e}", flush=True)
    return [x for e in names for x in chosen[e]]


party = {}
with open(OUT / "turns_party.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        party[r["pid"]] = (r.get("party", ""), r.get("side", ""))


def usable(r):
    return (1962 <= int(r["year"]) <= 1999 and not r["speaker"].upper().startswith(("AN HON", "HON", "SOME HON"))
            and len(r["text"].split()) >= MIN_WORDS)


pools = defaultdict(lambda: defaultdict(list))  # voice -> era -> rows
with open(OUT / "passages.jsonl", encoding="utf-8") as fh:
    for line in fh:
        r = json.loads(line)
        v = voice_of(r)
        if v and usable(r):
            r["voice"], r["era"] = v, era_of(int(r["year"]))
            pools[v][r["era"]].append(r)
for v in pools:
    for e in pools[v]:
        pools[v][e].sort(key=lambda r: r["pid"])

rnd = random.Random(SEED)
rows = []
for v in VOICES:
    rows += draw(pools[v], PER_CELL, rnd, v)

npools = defaultdict(list)
with open(OUT / "near_miss.jsonl", encoding="utf-8") as fh:
    for line in fh:
        r = json.loads(line)
        if usable(r):
            r["voice"], r["era"] = "near_miss", era_of(int(r["year"]))
            npools[r["era"]].append(r)
for e in npools:
    npools[e].sort(key=lambda r: r["pid"])
rows += draw(npools, NEAR_PER_ERA, random.Random(SEED), "near_miss")

random.Random(SEED).shuffle(rows)
cols = ["code_id", "pid", "voice", "era", "house", "date", "year", "speaker", "role", "party", "side", "text"]
for i, r in enumerate(rows, 1):
    r["code_id"] = f"V{i:03d}"
    r["party"], r["side"] = party.get(r["pid"], ("", ""))
    r["text"] = cap(r["text"])

VAL.mkdir(parents=True, exist_ok=True)
with open(VAL / "sample.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(VAL / "sample_blind.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["code_id", "text"], extrasaction="ignore"); w.writeheader(); w.writerows(rows)
strata = defaultdict(int)
for r in rows:
    strata[(r["voice"], r["era"])] += 1
with open(VAL / "sample_strata.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["voice", "era", "n"])
    for v in VOICES + ["near_miss"]:
        for e, _, _ in ERAS:
            w.writerow([v, e, strata[(v, e)]])

print("rows", len(rows))
print("voice x era counts")
for v in VOICES + ["near_miss"]:
    print(f"{v:10s}", " ".join(f"{e}={strata[(v, e)]:3d}" for e, _, _ in ERAS), " total", sum(strata[(v, e)] for e, _, _ in ERAS))
assert len(rows) == 550, len(rows)
assert len({r["pid"] for r in rows}) == len(rows), "duplicate pids"
print("OK: 550 rows, no duplicate pids")
