"""Draw the 2000-08 coding sample for the Indo-US nuclear deal extension (task E3): up to
PER_CELL passages per voice x period, coded the same way as the 1962-99 sample (two blind Claude
coders, Opus adjudication). The executive voice after 1999 is ministers in Parliament only (the
MEA Record in this corpus stops in 1999). Lok Sabha members are split by party family.

Periods: NDA (to 21 May 2004); UPA before the Joint Statement (to 17 July 2005); the deal
negotiated with the Left outside (to 8 July 2008); after the Left withdrew (to 31 Dec 2008).

Usage: python3 -I sample3.py OUTDIR VALIDATION_DIR
"""
import csv, json, random, re, sys
from collections import defaultdict
from pathlib import Path

OUT, VAL = Path(sys.argv[1]), Path(sys.argv[2])
SEED, PER_CELL, MIN_WORDS, CAP_WORDS = 20261103, 80, 25, 250
PERIODS = [("2000-04", "2000-01-01", "2004-05-22"), ("2004-05", "2004-05-22", "2005-07-18"),
           ("2005-08", "2005-07-18", "2008-07-09"), ("2008", "2008-07-09", "2009-01-01")]
VOICES = ["minister", "LS_left", "LS_bjp", "LS_congress", "LS_other", "RS_member"]
# copy of NUC in extract.py (keep in sync); used only to centre the 250-word cap
NUC = re.compile(r"\bnuclear\b|\batomic\b|\batom bombs?\b|\bNPT\b|\bCTBT\b|non-?\s?proliferation|"
                 r"pokh?a?ran|test[- ]ban|plutonium|fissile|परमाणु|आणविक|न्यूक्लियर|"
                 r"123 agreement|hyde act|civil nuclear|\bNSG\b|nuclear suppliers group|separation plan|IAEA", re.I)


def period_of(date):
    return next((p for p, a, b in PERIODS if a <= date < b), None)


def cap(text):
    words = text.split()
    if len(words) <= CAP_WORDS:
        return text
    hit = next((i for i, w in enumerate(words) if NUC.search(w)), 0)
    start = max(0, min(hit - CAP_WORDS // 2, len(words) - CAP_WORDS))
    return " ".join(words[start:start + CAP_WORDS])


party = {r["pid"]: r for r in csv.DictReader(open(OUT / "turns_party.csv", encoding="utf-8"))}


def voice_of(r):
    if r["house"] not in ("LS", "RS"):
        return None
    if r["role"] == "executive":
        return "minister"
    if r["role"] != "member":
        return None
    if r["house"] == "RS":
        return "RS_member"
    t = party.get(r["pid"], {})
    if t.get("family") == "Left":
        return "LS_left"
    if t.get("family") == "Jana Sangh / BJP":
        return "LS_bjp"
    if t.get("party") == "INC":
        return "LS_congress"
    return "LS_other"


pools = defaultdict(list)
for line in open(OUT / "passages.jsonl", encoding="utf-8"):
    r = json.loads(line)
    p = period_of(r["date"])
    if not p or r["speaker"].upper().startswith(("AN HON", "HON", "SOME HON")) or len(r["text"].split()) < MIN_WORDS:
        continue
    v = voice_of(r)
    if v:
        pools[(v, p)].append(r)

rnd = random.Random(SEED)
rows, strata = [], []
for v in VOICES:
    for p, _, _ in PERIODS:
        pool = sorted(pools[(v, p)], key=lambda r: r["pid"])
        pick = rnd.sample(pool, min(PER_CELL, len(pool)))
        for r in pick:
            r["voice"], r["era"] = v, p
        rows += pick
        strata.append({"voice": v, "period": p, "n": len(pick), "pool": len(pool)})

rnd.shuffle(rows)
for i, r in enumerate(rows, 1):
    t = party.get(r["pid"], {})
    r["code_id"] = f"X{i:04d}"
    r["party"], r["side"] = t.get("party", ""), t.get("side", "")
    r["text"] = cap(r["text"])
cols = ["code_id", "pid", "voice", "era", "house", "date", "year", "speaker", "role", "party", "side", "text"]
with open(VAL / "sample3.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(VAL / "sample3_blind.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["code_id", "text"], extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(VAL / "sample3_strata.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(strata[0])); w.writeheader(); w.writerows(strata)
print(len(rows), "passages")
for s in strata:
    print(s)
