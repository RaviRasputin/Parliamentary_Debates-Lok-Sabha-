"""Short human check of relevant passages only (author's request): 30 passages that take a
position on India's nuclear weapons posture, drawn across stances and voices from the model-coded
sample, excluding the 200-passage check. Selected on model codes, so results are read as
agreement within each stance, not as a population rate."""
import csv, json, random, sys
from collections import defaultdict
from pathlib import Path

VAL, DOCS = Path(sys.argv[1]), Path(sys.argv[2])
SEED = 20261102
QUOTA = {"pro_bomb": 6, "keep_option": 6, "disarmament": 6, "critical_of_tests": 6, "other_country": 3, "neutral": 3}
meta = {}
for name in ("sample.csv", "sample2.csv"):
    for r in csv.DictReader(open(VAL / name, encoding="utf-8")):
        meta[r["code_id"]] = r
used = {r["code_id"] for r in csv.DictReader(open(VAL / "human_check_sample.csv"))}
pools = defaultdict(list)
for name in ("gold.csv", "gold2.csv"):
    for g in csv.DictReader(open(VAL / name, encoding="utf-8")):
        m = meta[g["code_id"]]
        if g["relevant"] != "yes" or m["voice"] == "near_miss" or g["code_id"] in used:
            continue
        if g["stance"] == "neutral" and not (g["deterrence_weapon"] == "1" or g["option_open"] == "1"):
            continue  # neutral only when it is about weapons or the option
        if g["stance"] == "other_country" and g["deterrence_weapon"] != "1":
            continue
        pools[g["stance"]].append(g["code_id"])
rnd = random.Random(SEED)
picked = []
for st, q in QUOTA.items():
    pool = sorted(pools[st])
    by_voice = defaultdict(list)
    for c in pool:
        by_voice[meta[c]["voice"]].append(c)
    take = []
    voices = sorted(by_voice)
    while len(take) < q and any(by_voice.values()):  # round-robin across voices
        for v in voices:
            if by_voice[v] and len(take) < q:
                take.append(by_voice[v].pop(rnd.randrange(len(by_voice[v]))))
    picked += take
rnd.shuffle(picked)
with open(VAL / "human_check2_sample.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["check_id", "code_id", "voice", "year"])
    for i, c in enumerate(picked, 1):
        w.writerow([f"R{i:03d}", c, meta[c]["voice"], meta[c]["year"]])
DOCS.mkdir(parents=True, exist_ok=True)
for i, c in enumerate(picked, 1):
    json.dump({"code_id": f"R{i:03d}", "text": meta[c]["text"], "batches": ["check2"]}, open(DOCS / f"R{i:03d}.json", "w"))
print(len(picked))
