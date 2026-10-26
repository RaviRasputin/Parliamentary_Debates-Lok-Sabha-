"""Attach party, party family and government/opposition side to member turns.

Lok Sabha speakers are matched to election winners (DataMeet parliament.csv, from ECI results)
by constituency and name; Rajya Sabha speakers only by a unique name match against any
Lok Sabha winner, so Rajya Sabha coverage is partial.

Usage: python3 party.py OUTDIR parliament.csv
"""
import csv, re, sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

OUT, ELEC = Path(sys.argv[1]), sys.argv[2]
NO_PARTY_FROM = "2004-05-17"  # turns on or after this date get no party/side (later task)

# Lok Sabha in session -> election year whose winners sit in it (start date of each new House)
HOUSES = [("1967-03-16", 1962), ("1971-03-15", 1967), ("1977-03-25", 1971), ("1980-01-21", 1977),
          ("1985-01-15", 1980), ("1989-12-18", 1984), ("1991-07-09", 1989), ("1996-05-22", 1991),
          ("1998-03-23", 1996), ("1999-10-20", 1998), ("9999-12-31", 1999)]

# Government periods: (start, end, governing parties, outside supporters). Dates between periods
# with no stable majority (Charan Singh 1979-80, Chandra Shekhar 1990-91) are left unclassified.
GOVTS = [
    ("1962-01-01", "1977-03-24", {"INC"}, set()),
    ("1977-03-24", "1979-07-15", {"BLD"}, {"CPM"}),
    ("1980-01-14", "1989-12-02", {"INC(I)", "INC"}, set()),
    ("1989-12-02", "1990-11-07", {"JD", "TDP", "DMK", "AGP", "ICS(SCS)"}, {"BJP", "CPM", "CPI", "RSP", "FBL"}),
    ("1991-06-21", "1996-05-16", {"INC"}, set()),
    ("1996-05-16", "1996-06-01", {"BJP", "SHS", "SAP", "SAD", "HVP"}, set()),
    ("1996-06-01", "1998-03-19", {"JD", "SP", "TDP", "DMK", "TMC(M)", "AGP", "CPI"}, {"INC", "CPM", "RSP", "FBL"}),
    ("1998-03-19", "1999-10-13", {"BJP", "SHS", "SAP", "ADMK", "BJD", "WBTC", "SAD", "HLD(R)", "PMK", "MDMK"}, {"TDP"}),
    ("1999-10-13", "9999-12-31", {"BJP", "SHS", "JD(U)", "DMK", "AITC", "BJD", "SAD", "PMK", "MDMK", "INLD"}, {"TDP"}),
]

FAMILY = {
    "Congress": {"INC", "INC(I)", "INC(U)", "NCO", "ICS", "ICS(SCS)", "TMC(M)", "AIIC(T)", "WBTC", "AITC", "NCP", "ICJ"},
    "Jana Sangh / BJP": {"JS", "BJS", "BJP", "SHS"},
    "Left": {"CPI", "CPM", "RSP", "FB", "FBL", "PWP", "IPF"},
    "Socialist / Janata": {"PSP", "SSP", "SOC", "BLD", "JNP", "JNP(S)", "LKD", "JD", "SP", "SAP", "RJD", "JD(U)",
                           "JP", "BJD", "HLD(R)", "INLD", "SJP", "JD(G)"},
    "Swatantra": {"SWA"},
}
fam = {p: f for f, ps in FAMILY.items() for p in ps}
HON = re.compile(r"\b(SHRI|SHRIMATI|SMT|DR|PROF|KUMARI|SARDAR|CH|MAULANA|PANDIT|ACHARYA|MR|MRS|MISS|SYED|BEGUM|"
                 r"KUNWAR|RAJA|RANI|RAJMATA|MAHARAJA|SWAMI|ADV|ALIAS|SHRl|SHR1)\b\.?")


def toks(s):
    s = s.upper()
    if "," in s and "(" not in s:
        s = " ".join(reversed(s.split(",", 1)))
    s = HON.sub(" ", re.sub(r"\([^)]*\)?", " ", s.upper()))
    return tuple(t for t in re.split(r"[^A-Z]+", s) if t)


def _tok_sim(x, y):
    if len(x) > 1 and len(y) > 1:
        return SequenceMatcher(None, x, y).ratio()
    return 0.9 if x[0] == y[0] else 0


@lru_cache(maxsize=None)
def name_score(a, b):
    """Order-independent name similarity: the election file prints names as 'SAMAR GUHA',
    'G. SAMAR' or 'GUHA SAMAR', and the debates use initials freely. At least one full
    name part must match closely; every other part must match by name or initial."""
    if not a or not b:
        return 0
    def side(p, q):
        return [max(_tok_sim(x, y) for y in q) for x in p]
    sa, sb = side(a, b), side(b, a)
    full = [SequenceMatcher(None, x, y).ratio() for x in a for y in b if len(x) > 2 and len(y) > 2]
    if not full or max(full) < 0.75 or min(sa + sb) < 0.6:
        return 0
    return (sum(sa) / len(sa) + sum(sb) / len(sb)) / 2


def constituency(s):
    m = re.search(r"\(([^)]*)\)?", s)
    return re.sub(r"[^A-Z]", "", m.group(1).upper()) if m else ""


win = defaultdict(list)       # election year -> [(tokens, pc, party)]
for r in csv.DictReader(open(ELEC, encoding="utf-8", errors="ignore")):
    if r["#"] == "1":
        y = {"1985": "1984", "1992": "1991"}.get(r["YEAR"], r["YEAR"])
        win[int(y)].append((toks(r["NAME"]), re.sub(r"[^A-Z]", "", r["PC"].upper()), r["PARTY"]))
all_win = [w for y in win for w in win[y] if 1957 <= y <= 1999]


def build_index(ws):
    idx = defaultdict(list)
    for w in ws:
        for t in set(w[0]):
            if len(t) > 2:
                idx[t[:3]].append(w)
    return idx


def candidates(t, idx):
    seen, out = set(), []
    for x in t:
        if len(x) > 2:
            for w in idx.get(x[:3], ()):
                if id(w) not in seen:
                    seen.add(id(w)); out.append(w)
    return out


idx_e = {y: build_index(win[y]) for y in win}
idx_all = build_index(all_win)


@lru_cache(maxsize=None)
def pc_sim(a, b):
    return SequenceMatcher(None, a, b).ratio()


def house_for(date):
    return next(y for end, y in HOUSES if date < end)


cache = {}


def match_ls(speaker, date):
    e = house_for(date)
    t, pc = toks(speaker), constituency(speaker)
    key = (e, " ".join(t))
    if pc:
        best = None
        for wt, wpc, party in win[e]:
            if wpc and pc_sim(pc, wpc) >= 0.75:
                s = name_score(t, wt)
                if s >= 0.6 and (best is None or s > best[0]):
                    best = (s, party)
        if best:
            cache[key] = best[1]
            return best[1], "constituency"
    if key in cache:
        return cache[key], "cached"
    cands = [(name_score(t, wt), party) for wt, _, party in candidates(t, idx_e[e])]
    cands = sorted([c for c in cands if c[0] >= 0.88], reverse=True)
    if cands and (len(cands) == 1 or cands[0][0] - cands[1][0] > 0.05 or len({c[1] for c in cands[:3]}) == 1):
        cache[key] = cands[0][1]
        return cands[0][1], "name"
    return "", ""


def match_rs(speaker):
    t = toks(speaker)
    cands = sorted([(sc, party) for wt, _, party in candidates(t, idx_all) for sc in [name_score(t, wt)] if sc >= 0.92], reverse=True)
    if cands and len({c[1] for c in cands}) == 1:
        return cands[0][1], "name-any-LS"
    return "", ""


def side(party, date):
    for a, b, gov, out in GOVTS:
        if a <= date < b:
            if not party:
                return "unknown"
            return "government" if party in gov else "outside support" if party in out else "opposition"
    return "unclassified period"


rows = list(csv.DictReader(open(OUT / "turns.csv", encoding="utf-8")))
rs_cache = {}
for r in rows:
    r["party"] = r["match"] = r["family"] = r["side"] = ""
    if r["house"] not in ("LS", "RS") or r["role"] != "member":
        continue
    if r["speaker"].upper().startswith(("AN HON", "HON", "SOME HON")):
        continue
    if r["date"] >= NO_PARTY_FROM:  # 2004 House and UPA periods are not yet labelled
        continue
    if r["house"] == "LS":
        p, how = match_ls(r["speaker"], r["date"])
    else:
        k = " ".join(toks(r["speaker"]))
        if k not in rs_cache:
            rs_cache[k] = match_rs(r["speaker"])
        p, how = rs_cache[k]
    r["party"], r["match"] = p, how
    r["family"] = fam.get(p, "Other / regional" if p and p != "IND" else ("Independent" if p == "IND" else ""))
    r["side"] = side(p, r["date"])

with open(OUT / "turns_party.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# coverage report
cov = defaultdict(Counter)
for r in rows:
    if r["role"] == "member" and r["house"] in ("LS", "RS"):
        cov[r["house"]]["all"] += 1
        cov[r["house"]]["matched" if r["party"] else "unmatched"] += 1
for h in cov:
    c = cov[h]; print(h, dict(c), f"{100 * c['matched'] / c['all']:.1f}% matched")
print(Counter(r["match"] for r in rows if r["match"]))
