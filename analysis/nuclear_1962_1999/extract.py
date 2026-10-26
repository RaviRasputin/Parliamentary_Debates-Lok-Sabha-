"""Extract nuclear-related speech turns from Lok Sabha / Rajya Sabha debates,
the MEA Foreign Affairs Record and SWJN (1962-64), and code them by frame.

Usage: python3 extract.py ROOT OUTDIR [START END]
"""
import csv, json, re, sys, zipfile
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
START, END = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1962, 1999)

NUC = re.compile(r"\bnuclear\b|\batomic\b|\batom bombs?\b|\bNPT\b|\bCTBT\b|non-?\s?proliferation|"
                 r"pokh?a?ran|test[- ]ban|plutonium|fissile|परमाणु|आणविक|न्यूक्लियर", re.I)

FRAMES = {
    "disarmament": r"disarmament|test[- ]ban|elimination of (all )?nuclear weapons|nuclear[- ]weapons?[- ]free|"
                   r"ban(ning)? (on )?(all )?nuclear (tests|weapons)|six[- ]nation|delhi declaration|action plan",
    "peaceful_use": r"peaceful (purposes?|uses?|applications?|nuclear explosions?|explosions?|programme)|"
                    r"atoms? for peace|nuclear power (stations?|plants?|projects?|reactors?)|power reactors?|"
                    r"generation of (electricity|power)",
    "option_open": r"options? (is |are |remains? |kept )?open|keep(ing|s)? (our|the|its|their|this) (nuclear )?options?|"
                   r"nuclear option|foreclose|freedom of (action|choice)",
    "discrimination": r"discriminat\w*|apartheid|have[- ]nots?\b|nuclear haves|unequal|inequitable|hegemon\w*|"
                      r"monopoly|vertical proliferation|club",
    "deterrence_weapon": r"deterren\w*|deterrent|weaponi[sz]\w*|(make|making|manufacture|manufacturing|produce|"
                         r"producing|go in for|going in for|develop|developing|build|building) (the |an |our own |a |"
                         r"our )?(atom(ic)? |nuclear )?bombs?|nuclear weapons? (programme|capabilit\w+|power)|"
                         r"nuclear[- ]weapons? states?|no[- ]first[- ]use|second strike|arsenal",
    "security_threat": r"\bchina\b|chinese|pakistan\w*|\bthreat\w*|national security|security (environment|"
                       r"concerns?|interests?|needs?)|blackmail|umbrella|guarantee",
    "autonomy": r"sovereign\w*|self[- ]reliance|national interest|pressures?\b|sanctions?\b|"
                r"independen(t|ce) of (judgment|action|decision)|dictat\w*|coerc\w*|bow down|surrender",
}
FRAME_RX = {k: re.compile(v, re.I) for k, v in FRAMES.items()}
META = {"consensus": re.compile(r"consensus", re.I)}

PHRASES = {
    "keep option open": r"keep(ing|s)? (our|the|its) (nuclear )?options? open|options? (is |are |remains? )?open",
    "nuclear option": r"nuclear option",
    "discriminatory treaty": r"discriminatory (treaty|character|nature|regime)|treaty (is|was) discriminatory",
    "nuclear apartheid": r"nuclear apartheid",
    "haves and have-nots": r"have[- ]nots|nuclear haves",
    "peaceful nuclear explosion": r"peaceful nuclear explosions?",
    "minimum deterrent": r"minimum (credible )?(nuclear )?deterren\w*|credible minimum",
    "no first use": r"no[- ]first[- ]use",
    "nuclear weapon state": r"nuclear[- ]weapons?[- ]states?",
    "national consensus": r"national consensus",
    "weaponisation": r"weaponi[sz]\w*",
    "CTBT": r"\bCTBT\b|comprehensive (nuclear )?test[- ]ban",
    "NPT": r"\bNPT\b|non-?\s?proliferation treaty",
}
PHRASE_RX = {k: re.compile(v, re.I) for k, v in PHRASES.items()}
QUOTE_KEYS = {"keep option open", "nuclear apartheid", "discriminatory treaty", "national consensus",
              "minimum deterrent", "haves and have-nots", "no first use", "weaponisation"}

HON = r"(?:(?i:SHRI|SHRIMATI|SMT\.|DR\.|PROF\.|KUMARI|SARDAR|CH\.|MAULANA|PANDIT|ACHARYA|RAJMATA|MAHARAJA|SWAMI|MRS\.|MISS|SYED|BEGUM|KUNWAR|RAJA|RANI)|MR\.|Mr\.)"
LABEL = re.compile(
    r"(?P<lab>"
    r"(?P<exec>(?:THE\s+|The\s+)?(?i:DEPUTY\s+PRIME\s+MINISTER|PRIME\s+MINISTER|(?:DEPUTY\s+)?MINISTER(?:\s+OF\s+STATE)?|"
    r"LEADER\s+OF\s+THE\s+HOUSE)[A-Za-z ,.&'\-]{0,140}?\((?P<ename>[^()]{3,70})\))"
    r"|(?P<chair>(?i:MR\.|MADAM|THE)\s+(?i:DEPUTY[- ])?(?i:SPEAKER|CHAIRMAN)|(?i:THE\s+VICE[- ]CHAIRMAN)(?:\s*\([^()]{0,60}\))?)"
    r"|(?P<mem>" + HON + r"\s+[A-Z][A-Za-z.'\-]*(?:\s+[A-Z][A-Za-z.'\-]*){0,5}(?:\s*\([^()]{2,60}\))?)"
    r"|(?P<hon>(?i:AN\s+HON\.?\s+MEMBER|HON\.?\s+MEMBERS|SOME\s+HON\.?\s+MEMBERS))"
    r")\s*:")
DATE_LS = re.compile(r"^## (\d{4}-\d{2}-\d{2})", re.M)
DATE_RS = re.compile(r"^## (\d{1,2} \w+ \d{4})", re.M)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def norm_name(s):
    s = re.sub(r"\([^)]*\)", " ", s).upper()
    s = re.sub(r"\b(SHRI|SHRIMATI|SMT|DR|PROF|KUMARI|SARDAR|CH|MAULANA|PANDIT|ACHARYA|MR|MRS|MISS)\b\.?", " ", s)
    return re.sub(r"[^A-Z]", "", s)


def windows(text, span=60):
    """Return text within +-span words of any nuclear keyword, plus keyword hit count."""
    words = text.split()
    hits = [i for i, w in enumerate(words) if NUC.search(w)]
    if not hits:
        # multi-word keywords (atom bomb, test ban) are caught on the joined text
        if not NUC.search(text):
            return "", 0
        hits = [len(text[:m.start()].split()) for m in NUC.finditer(text)]
    keep = set()
    for i in hits:
        keep.update(range(max(0, i - span), min(len(words), i + span + 1)))
    return " ".join(words[i] for i in sorted(keep)), len(hits)


def code(text):
    f = {k: len(rx.findall(text)) for k, rx in FRAME_RX.items()}
    f.update({k: len(rx.findall(text)) for k, rx in META.items()})
    p = {k: len(rx.findall(text)) for k, rx in PHRASE_RX.items()}
    return f, p


def sittings(house, year):
    if house == "LS":
        z = ROOT / "Parliamentary_Debates-Lok-Sabha-" / "data" / f"{year}.zip"
    else:
        z = ROOT / "Parliamentary_Debates-Rajya-Sabha-" / "data" / f"{year}.zip"
    if not z.exists():
        return
    with zipfile.ZipFile(z) as zf:
        raw = zf.read(zf.namelist()[0]).decode("utf-8", "ignore")
    rx = DATE_LS if house == "LS" else DATE_RS
    ms = list(rx.finditer(raw))
    for i, m in enumerate(ms):
        body = raw[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(raw)]
        d = m.group(1)
        if house == "RS":
            dd, mon, yy = d.split()
            d = f"{yy}-{MONTHS.get(mon.lower(), 0):02d}-{int(dd):02d}"
        yield d, re.sub(r"\s+", " ", body)


def process_house_year(args):
    house, year = args
    exec_since = {}  # normalized name -> first date seen speaking as a minister
    turns, words_total = [], 0
    for date, text in sittings(house, year):
        words_total += len(text.split())
        ms = list(LABEL.finditer(text))
        for i, m in enumerate(ms):
            seg = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
            if m.group("exec"):
                role, name = "executive", m.group("ename")
                key = norm_name(name)
                exec_since.setdefault(key, date)
                office = re.sub(r"\s+", " ", m.group("exec").split("(")[0]).strip()
            elif m.group("chair"):
                role, name, office = "chair", m.group("chair"), ""
            elif m.group("mem"):
                name, office = m.group("mem"), ""
                key = norm_name(name)
                role = "executive" if key in exec_since and exec_since[key] <= date else "member"
            else:
                role, name, office = "member", m.group("hon"), ""
            if role == "chair" or not NUC.search(seg):
                continue
            win, nhits = windows(seg)
            if not nhits:
                continue
            f, p = code(win)
            turns.append({"house": house, "year": year, "date": date, "role": role,
                          "speaker": re.sub(r"\s+", " ", name).strip()[:80], "office": office[:80],
                          "nuc_hits": nhits, "words": len(seg.split()), **f,
                          **{"ph_" + k: v for k, v in p.items()}, "_win": win})
    return house, year, words_total, turns


def process_doc(args):
    source, year, path = args
    raw = re.sub(r"\s+", " ", Path(path).read_text("utf-8", "ignore"))
    total = len(raw.split())
    # chunk into ~400-word pseudo-documents so frame counts are comparable to speech turns
    words = raw.split()
    out = []
    for s in range(0, len(words), 400):
        seg = " ".join(words[s:s + 400])
        win, nhits = windows(seg)
        if not nhits:
            continue
        f, p = code(win)
        out.append({"house": source, "year": year, "date": str(year), "role": "executive",
                    "speaker": source, "office": "", "nuc_hits": nhits, "words": 400, **f,
                    **{"ph_" + k: v for k, v in p.items()}, "_win": win})
    return source, year, total, out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(h, y) for y in range(START, END + 1) for h in ("LS", "RS")]
    docs = []
    for y in range(START, END + 1):
        p = ROOT / "Foreign_Affairs_Record-MEA-1955-1999" / f"{y}.md"
        if p.exists():
            docs.append(("MEA", y, str(p)))
    swjn_years = {75: 1962, 76: 1962, 77: 1962, 78: 1962, 79: 1962, 80: 1962, 81: 1963, 82: 1963, 83: 1963,
                  84: 1963, 85: 1964}
    for v, y in swjn_years.items():
        p = ROOT / "Selected_Works_of_JLN" / "second_series" / f"SWJLN_S2_V{v}.md"
        if p.exists() and START <= y <= END:
            docs.append(("SWJN", y, str(p)))

    rows, sizes = [], []
    with Pool(4) as pool:
        for src, y, total, t in pool.imap_unordered(process_house_year, jobs):
            sizes.append({"source": src, "year": y, "words": total}); rows += t
            print(src, y, total, len(t), flush=True)
        for src, y, total, t in pool.imap_unordered(process_doc, docs):
            sizes.append({"source": src, "year": y, "words": total}); rows += t
    rows.sort(key=lambda r: (r["year"], r["house"], r["date"]))

    cols = [k for k in rows[0] if k != "_win"]
    with open(OUT / "turns.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    with open(OUT / "corpus_sizes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["source", "year", "words"]); w.writeheader()
        w.writerows(sorted(sizes, key=lambda r: (r["year"], r["source"])))
    # quotes: every passage containing a key phrase, for close reading
    with open(OUT / "quotes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["phrase", "house", "date", "role", "speaker", "excerpt"])
        for r in rows:
            for k in QUOTE_KEYS:
                for m in PHRASE_RX[k].finditer(r["_win"]):
                    a, b = max(0, m.start() - 500), min(len(r["_win"]), m.end() + 300)
                    w.writerow([k, r["house"], r["date"], r["role"], r["speaker"], r["_win"][a:b]])
    print("turns", len(rows))


if __name__ == "__main__":
    main()
