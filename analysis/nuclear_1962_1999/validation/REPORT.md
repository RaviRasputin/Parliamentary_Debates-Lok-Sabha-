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

Validated series under codebook 1.0, all nuclear topics (`series_gap_broad.csv`, frame JSD, 90% bootstrap CI):

| Era | MEA vs members | Ministers vs members |
| --- | --- | --- |
| 1962–68 | 0.30 (0.25–0.40) | 0.05 |
| 1969–79 | 0.32 (0.26–0.40) | 0.10 |
| 1980–89 | 0.29 (0.23–0.39) | 0.01 |
| 1990–93 | 0.25 (0.20–0.34) | 0.13 |
| 1994–97 | 0.14 (0.10–0.22) | 0.02 |
| 1998–99 | 0.12 (0.09–0.17) | 0.04 |

The 550-passage check above (1990–97 as one era) understated the 1994–97 narrowing; the scaled series supersedes it. Keep-the-option stance peaks in every voice in 1994–97 (MEA 17%, ministers 13%, members 10% of relevant passages). In 1998–99 the MEA is 40% pro-bomb; members split 36 pro-bomb vs 40 critical of the tests. Dictionary F1 on the full set: 0.39–0.82 (`dictionary_performance_full.csv`).

---

# Weapons-and-security scope (codebook 1.1)

The author's first 22 human-check codes marked nuclear-energy, plant and uranium-trade passages not relevant. The author then set the scope to weapons and security only. The rule is applied to the existing adjudicated codes (no recoding): a passage stays relevant if its stance is pro-bomb, keep-option, disarmament or critical-of-tests, or it carries a disarmament, option-open, discrimination, deterrence or security-threat frame. 1,090 of the 1,990 relevant passages remain. These are now the main series (`series_gap.csv`, `series_stance.csv`, `series_frames.csv`, `series_sides.csv`); the broad ones are kept as `*_broad.csv`.

| Era | n (MEA / members / ministers) | Frames: MEA vs members | Frames: ministers vs members | Stance: MEA vs members |
| --- | --- | --- | --- | --- |
| 1962–68 | 95 / 102 / 31 | 0.34 (0.27–0.43) | 0.04 | 0.26 |
| 1969–79 | 84 / 61 / 13 | 0.36 (0.29–0.46) | 0.17 | 0.33 |
| 1980–89 | 90 / 56 / 20 | 0.18 (0.12–0.27) | 0.05 | 0.17 |
| 1990–93 | 61 / 65 / 17 | 0.26 (0.20–0.38) | 0.32 | 0.30 |
| 1994–97 | 72 / 66 / 26 | 0.06 (0.03–0.12) | 0.04 | 0.19 |
| 1998–99 | 68 / 124 / 39 | 0.08 (0.05–0.12) | 0.03 | 0.30 |

What changes: the frame convergence of 1994–97 is sharper (0.06 against 0.14 broad) and holds in 1998–99; the 1980s are closer than the broad series showed (0.18), because energy talk had kept members apart from the MEA's disarmament language. Keep-the-option now rises from 1990 in the executive (ministers 35%, MEA 21% in both 1990–93 and 1994–97) and reaches members only in 1994–97 (24%). The stance gap still does not close (0.30 in 1998–99). Ministers' cells are small (13–39 passages), and only three government/opposition cells reach the minimum size, so the side analysis is reported only for 1962–68 and 1998–99.

Human check rescored (22 codes, model relevance under 1.1): relevance agreement 81.8% (alpha 0.49), up from 54.5% (alpha 0.08) under 1.0. Stance and frames rest on 3 passages and are not yet informative; the 30-passage relevant-only check (R001–R030) is for those.

---

# Human check of 30 relevant passages (R001–R030)

The author coded 29 of the 30 passages blind (R011 left uncoded); scored with `human_check.py` (`human_check2_results.csv`, `human_check2_agreement.csv`).

| Field | n | Agreement | Alpha |
| --- | --- | --- | --- |
| Relevant | 29 | 72% | n/a (the model said yes to all 30, by design of the sample) |
| Stance | 21 | 24% | 0.11 |
| Frames | 21 | 43% (option open) to 76% (disarmament, deterrence) | −0.18 to 0.53 |

Review by Claude (`human_check2_review.csv`). Claude read each passage against the codebook with both codes in view, so this is not an independent third coder and may share the model coders' blind spots. Of 29 passages, the two codes agreed on 5; the review sided with the model on 22, with the author on 1 (R030, a one-line interjection), and with neither on 1 (R025, a factual answer on the test moratorium, ruled neutral). The recurring differences:

- **Relevance of short or Hindi passages.** The author marked as not relevant a Hindi speech praising the refusal to sign the NPT (R012), a ruling against nuclear-armed warships in Indian ports (R003) and the Lahore risk-reduction text (R017). All are weapons topics under codebook 1.1.
- **Peaceful-only for criticism.** Speeches that attack the tests (R005, R029) or restate NPT objections (R023) were coded peaceful only.
- **Defences of the tests coded neutral or other-country** (R004, R006), which the codebook puts under pro-bomb.
- **More frames per passage** (2.9 against 1.9). Peaceful use was marked in 11 of 21 passages (model 1) and option open in 13 (model 3).

The check did turn up one fault in the pipeline, not in the coding. Two "minister" passages from 1998 (R028, R029) are opposition speeches. Two causes:
- a plain-name turn kept ministerial status for the rest of the calendar year, even after the government changed;
- a run-on sentence ending in "…Minister" followed by a member's label ("SHRI SUSHIL KUMAR SHINDE (Solapur):") was read as a minister's label.

Both are fixed in `extract.py`. `revoice.py` re-derives every coded passage's voice from the new extraction. The codes are blind to voice, so they stand.

After the fix (fresh `extract.py` run, `party.py`, `party_analysis.py`, then `revoice.py`; `voice_fix.csv`), 14 of the 750 coded ministerial passages became members' passages: 7 Lok Sabha and 7 Rajya Sabha, among them Pranab Mukherjee in 1996, Basudeb Acharia in 1995 and Sushil Kumar Shinde in 1998. R029 (Som Pal, 1998) stays ministerial: he was a minister of state in the government at the time. The weapons-and-security series barely moves:
- MEA vs members: 0.33, 0.36, 0.17, 0.26, 0.06, 0.08;
- ministers vs members: 0.02, 0.17, 0.05, 0.34, 0.03, 0.03;
- stance, MEA vs members: 0.25, 0.33, 0.16, 0.30, 0.20, 0.31.

Dictionary outputs change only in the third decimal.

---

# The Indo-US deal, 2000–08 (codebook 1.2; `e3.py`)

**Sample.** `sample3.py` drew 1,493 parliamentary passages from 2000–08: up to 80 per voice and period. The voices are ministers (both houses), Lok Sabha Left, BJP (with Shiv Sena), Congress and other members, and Rajya Sabha members. The periods are NDA to 21 May 2004; UPA to 17 July 2005; the deal years to 8 July 2008; after the Left withdrew. Small cells took every passage they had. Party labels for the 14th Lok Sabha come from DataMeet's 2004 results (`party.py`). After 1999 the executive voice is ministers in Parliament only, because the MEA Record in this corpus stops in 1999.

**Coding.** The same two blind Claude coders coded the sample, in isolated batches. The 200 passages with any disagreement went to four Opus adjudicators, who wrote 327 rulings (`adjudication3.csv`). Codebook 1.2 adds a `deal_stance` variable and counts deal passages as relevant even when they argue only about energy.

**Agreement (alpha):**
- relevant 0.97;
- stance 0.91;
- deal_stance 0.96;
- frames 0.67 (discrimination) to 0.85.

Of the 1,493 passages, 474 are relevant. Ministers are thin: only 9, 9, 23 and 17 relevant passages across the four periods. Most ministerial nuclear passages in these years are about energy and plants, not weapons or the deal.

**Results (`e3_gap.csv`, `e3_deal.csv`, `e3_stance.csv`, `e3_frames.csv`):**

| Period | Frame JSD, ministers vs all members | Deal-stance JSD, ministers vs all members |
| --- | --- | --- |
| 2000–04 (NDA) | 0.07 | — |
| 2004–05 (UPA) | 0.04 | 0.00 (almost no deal talk) |
| 2005–08 (deal) | 0.06 | 0.50 (0.42–0.59) |
| Jul–Dec 2008 | 0.17 | 0.60 (0.49–0.73) |

Deal stance by voice, 2005–08 / Jul–Dec 2008 (support–oppose–conditional):

| Voice | 2005–08 | Jul–Dec 2008 |
| --- | --- | --- |
| Ministers | 8–0–0 | 10–0–0 |
| Congress members | 12–0–0 | 2–0–0 |
| Left | 0–22–4 | 0–3–1 |
| BJP | 2–12–2 | 0–19–1 |
| Rajya Sabha members | 6–17–3 | 0–2–0 |

**Frames, 2005–08:**
- Ministers spoke mostly of peaceful use (52% of frame uses) and autonomy (22%).
- The Left spoke of autonomy (51%) and peaceful use (28%), never of security threats.
- The BJP spoke of autonomy (33%), security (25%), the option (11%) and deterrence (8%). Eight BJP passages took a keep-the-option stance, on the right to test.

H7 is supported on position, and the deal reopened the gap. The executive's framing stayed close to the House until the Left left (frame JSD 0.04–0.07, rising to 0.17 after July 2008). Members split sharply on the deal itself, and the two oppositions opposed it for different reasons: the Left on sovereignty and alignment with the US, the BJP on autonomy and on the weapons programme and testing. Ministerial cells are small, so the frame gaps carry wide intervals.
