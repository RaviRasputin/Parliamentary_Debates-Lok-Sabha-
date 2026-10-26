"""Draw the scaled coding sample: 125 passages per voice x era over six eras (1962-99),
counting the passages already in validation/sample.csv, so the combined set can rebuild the
gap series on Claude-coded, Opus-adjudicated codes. No top-up across eras: a short cell takes
everything it has.

Usage: python3 -I sample2.py OUTDIR VALIDATION_DIR
"""
import csv, json, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

OUT, VAL = Path(sys.argv[1]), Path(sys.argv[2])
SEED, PER_CELL, MIN_WORDS, CAP_WORDS = 20261027, 125, 25, 250
ERAS = [("1962-68", 1962, 1968), ("1969-79", 1969, 1979), ("1980-89", 1980, 1989),
        ("1990-93", 1990, 1993), ("1994-97", 1994, 1997), ("1998-99", 1998, 1999)]
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
    if r["house"] in ("LS", "RS"):
        if r["role"] == "executive":
            return "minister"
        if r["role"] == "member":
            return r["house"] + "_member"
    return None


def cap(text):
    words = text.split()
    if len(words) <= CAP_WORDS:
        return text
    hit = next((i for i, w in enumerate(words) if NUC.search(w)), 0)
    start = max(0, min(hit - CAP_WORDS // 2, len(words) - CAP_WORDS))
    return " ".join(words[start:start + CAP_WORDS])


old = [r for r in csv.DictReader(open(VAL / "sample.csv", encoding="utf-8")) if r["voice"] != "near_miss"]
taken = {r["pid"] for r in old}
have = Counter((r["voice"], era_of(int(r["year"]))) for r in old)

pools = defaultdict(list)
for line in open(OUT / "passages.jsonl", encoding="utf-8"):
    r = json.loads(line)
    y = int(r["year"])
    v = voice_of(r)
    if (v and 1962 <= y <= 1999 and r["pid"] not in taken
            and not r["speaker"].upper().startswith(("AN HON", "HON", "SOME HON"))
            and len(r["text"].split()) >= MIN_WORDS):
        pools[(v, era_of(y))].append(r)

rnd = random.Random(SEED)
rows, strata = [], []
for v in VOICES:
    for e, _, _ in ERAS:
        pool = sorted(pools[(v, e)], key=lambda r: r["pid"])
        need = max(0, PER_CELL - have[(v, e)])
        pick = rnd.sample(pool, min(need, len(pool)))
        for r in pick:
            r["voice"], r["era"] = v, e
        rows += pick
        strata.append({"voice": v, "era": e, "already": have[(v, e)], "new": len(pick),
                       "total": have[(v, e)] + len(pick), "pool": len(pool)})
        if have[(v, e)] + len(pick) < PER_CELL:
            print(f"SHORT {v} {e}: {have[(v, e)] + len(pick)} of {PER_CELL}")

party = {}
for r in csv.DictReader(open(OUT / "turns_party.csv", encoding="utf-8")):
    party[r["pid"]] = (r.get("party", ""), r.get("side", ""))
random.Random(SEED).shuffle(rows)
for i, r in enumerate(rows, 1):
    r["code_id"] = f"W{i:04d}"
    r["party"], r["side"] = party.get(r["pid"], ("", ""))
    r["text"] = cap(r["text"])
cols = ["code_id", "pid", "voice", "era", "house", "date", "year", "speaker", "role", "party", "side", "text"]
with open(VAL / "sample2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(VAL / "sample2_blind.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["code_id", "text"], extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(VAL / "sample2_strata.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(strata[0])); w.writeheader(); w.writerows(strata)
print(len(rows), "new passages")
for s in strata:
    print(s)
