# Validation report (task A4), 26 October 2026

**Coding design.** 550 passages: 125 each for Lok Sabha members, Rajya Sabha members, ministers and the MEA Record (25 per era), plus 50 near-miss passages. Coded blind (text only) with codebook v1.0 by two independent Claude coders, A and B. 101 passages had at least one disagreement; Opus adjudicated each field with a written reason (`adjudication.csv`, 141 rulings). The author chose not to hand-code. **No human coding is involved**, and the paper must say so.

Two batches (A4 and B3) were discarded and re-coded in isolated folders after the coders reported touching a shared scratch folder (`codes_*` are the clean re-codes).

## Agreement between the Claude coders (Krippendorff's alpha, 95% bootstrap CI)

| Field | Units | Agreement | Alpha |
| --- | --- | --- | --- |
| Relevant | 550 | 98.2% | 0.96 (0.94–0.98) |
| Disarmament | 335 | 96.4% | 0.91 (0.86–0.96) |
| Peaceful use | 335 | 97.9% | 0.96 (0.92–0.98) |
| Option open | 335 | 97.9% | 0.75 (0.52–0.91) |
| Discrimination | 335 | 97.6% | 0.85 (0.73–0.94) |
| Deterrence, weapons | 335 | 94.9% | 0.84 (0.76–0.91) |
| Security threat | 335 | 95.5% | 0.88 (0.81–0.93) |
| Autonomy | 335 | 94.0% | 0.73 (0.60–0.83) |
| Stance | 335 | 90.1% | 0.86 (0.81–0.90) |

## Dictionary performance against the adjudicated codes (335 relevant nuclear passages)

| Frame | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Disarmament | 0.87 | 0.74 | 0.80 |
| Security threat | 0.57 | 0.74 | 0.64 |
| Discrimination | 0.46 | 0.62 | 0.53 |
| Autonomy | 0.54 | 0.42 | 0.48 |
| Peaceful use | 0.84 | 0.33 | 0.47 |
| Option open | 0.63 | 0.33 | 0.44 |
| Deterrence, weapons | 0.48 | 0.39 | 0.43 |

Keyword filter: 335 of 500 keyword-selected passages (67%) are relevant; the rest are headings, lists and passing mentions. 7 of 50 near-miss passages are relevant (the filter misses some).

**Only the disarmament frame meets the usual bar (F1 ≥ 0.7). The other six are flagged as weak.**

## The gap re-measured with the adjudicated codes (sample only; `gap_validation.csv`)

| Era | MEA vs members, adjudicated codes (90% CI) | Same passages, dictionary |
| --- | --- | --- |
| 1962–68 | 0.36 (0.27–0.54) | 0.06 |
| 1969–79 | 0.33 (0.26–0.55) | 0.27 |
| 1980–89 | 0.44 (0.33–0.67) | 0.28 |
| 1990–97 | 0.37 (0.26–0.60) | 0.11 |
| 1998–99 | 0.10 (0.07–0.24) | 0.06 |

With validated codes the gap stays wide until 1997 and closes only in 1998–99. The dictionary measure placed the closing in 1994–97. Cells are small (19–40 passages per voice and era), so this is a check, not a replacement series.

Stance (`stance_by_voice_era.csv`): the MEA's passages are mostly disarmament in 1962–89 (12–13 of about 20 per era), fall to 4 of 20 in 1990–97 (mostly neutral) and include 7 pro-bomb of 21 in 1998–99. Members' passages are mostly neutral; pro-bomb rises from 0–4 per era before 1998 to 9 of 40 in 1998–99, with 7 critical of the tests.

---

# Scaled validated series (2,954 passages)

`sample2.py` drew 2,454 more passages so that each voice has about 125 per era over six eras (1962–68, 1969–79, 1980–89, 1990–93, 1994–97, 1998–99); with the first sample, 2,954 passages (1,990 relevant). The same two Claude coders coded them blind in isolated batches; 523 passages with disagreements were adjudicated by six Opus adjudicators following `CODEBOOK.md` and `adjudication.csv` as precedent (`adjudication2.csv`, 814 rulings). One coder batch (A12) wrote not-relevant rows with an extra empty column; those 56 rows were repaired at merge (codes unaffected).

Agreement (Krippendorff's alpha): relevant 0.94, stance 0.88, frames 0.62 (option open) to 0.96 (peaceful use).

Validated series (`series_gap.csv`, frame JSD, 90% bootstrap CI):

| Era | MEA vs members | Ministers vs members |
| --- | --- | --- |
| 1962–68 | 0.30 (0.25–0.40) | 0.05 |
| 1969–79 | 0.32 (0.26–0.40) | 0.10 |
| 1980–89 | 0.29 (0.23–0.39) | 0.01 |
| 1990–93 | 0.25 (0.20–0.34) | 0.13 |
| 1994–97 | 0.14 (0.10–0.22) | 0.02 |
| 1998–99 | 0.12 (0.09–0.17) | 0.04 |

The 550-passage check above (1990–97 as one era) understated the 1994–97 narrowing; the scaled series supersedes it. Keep-the-option stance peaks in every voice in 1994–97 (MEA 17%, ministers 13%, members 10% of relevant passages). In 1998–99 the MEA is 40% pro-bomb; members split 36 pro-bomb vs 40 critical of the tests. Dictionary F1 on the full set: 0.39–0.82 (`dictionary_performance_full.csv`).
