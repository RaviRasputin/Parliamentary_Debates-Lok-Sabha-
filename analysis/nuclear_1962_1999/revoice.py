"""Re-derive the voice (minister / LS_member / RS_member) and Lok Sabha party side of every coded
passage from a fresh extraction, after the speaker-role fix of 26 October 2026 (ministerial status
of plain-name turns now lapses when the government changes; run-on 'Minister ... SHRI X (Seat)'
labels are members). Codes are blind to voice, so they stand; only the grouping changes.

Usage: python3 -I revoice.py OUTDIR VALDIR
Writes VALDIR/voice_fix.csv (code_id, pid, old_voice, voice, speaker, party, side).
"""
import csv, sys
from collections import Counter
from pathlib import Path

OUT, VAL = Path(sys.argv[1]), Path(sys.argv[2])
turns = {r["pid"]: r for r in csv.DictReader(open(OUT / "turns_party.csv", encoding="utf-8"))}
rows, moves = [], Counter()
for name in ("sample.csv", "sample2.csv"):
    for s in csv.DictReader(open(VAL / name, encoding="utf-8")):
        if s["voice"] in ("MEA", "near_miss"):
            continue
        t = turns[s["pid"]]
        v = "minister" if t["role"] == "executive" else t["house"] + "_member"
        moves[(s["voice"], v)] += 1
        rows.append({"code_id": s["code_id"], "pid": s["pid"], "old_voice": s["voice"], "voice": v,
                     "speaker": t["speaker"], "party": t.get("party", ""), "side": t.get("side", "")})
with open(VAL / "voice_fix.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for (a, b), n in sorted(moves.items()):
    print(f"{a:10} -> {b:10} {n}")
