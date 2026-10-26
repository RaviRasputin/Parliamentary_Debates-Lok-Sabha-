# CLAUDE.md: the nuclear "gap" paper

Guide for Claude Code sessions working in this folder. Read it before changing anything.

## The project

A research paper: *Closing the Gap: Executive Secrecy, Parliamentary Debate and the Convergence
of India's Nuclear Position, 1962–2008*. Author: Ravi (repository owner). It measures how far
apart India's secret executive and the public legislature were on nuclear policy. Two
comparisons carry it:
- ministers vs members in Parliament;
- the MEA *Foreign Affairs Record* vs members.

The measure is the Jensen–Shannon divergence of frame and stance distributions, built on
LLM-coded, adjudicated passages.

- Paper (finished draft): `paper/closing_the_gap.md` (figures in `paper/figures/`),
  `paper/closing_the_gap.docx`. The live, editable version is a Claude Docs document:
  https://claude.ai/artifact/AKHUDzsPAWhy6abQpzCkfe (its "Path to publication" and "Research plan"
  tabs are older; `paper/PUBLICATION.md` and `PLAN.md` are current).
- Publication checklist and journals: `paper/PUBLICATION.md`.
- Human-check coding page (Claude artifact with a shared database):
  https://claude.ai/artifact/7oLL3AosHigigFCutTJEeS. Source: `tools/passage_coder.html`.
- Plan and status: `PLAN.md`. Validation write-up: `validation/REPORT.md`. Codebook:
  `validation/CODEBOOK.md` (v1.2).

## Standing instructions from the author

- **Ask the author before any decision the plan does not cover.** Do not choose scope,
  sources, relevance rules or coding categories on your own.
- Coding is done by Claude, not by the author: two blind coders, with Opus adjudicating
  disagreements. The author checks samples by hand.
- Relevance for the analysis is **weapons and security only** (author's decision; codebook 1.1).
  Energy-only passages are out, except passages about the Indo-US deal in 2000–08 (codebook 1.2).
- Nehru's Selected Works are dropped. The comparison is executive vs legislature for every
  government alike.
- Only online archives; no archive visits.
- Write plainly: short sentences, no jargon, no rhetorical flourishes.

## Layout

| Path | What it is |
| --- | --- |
| `extract.py` | Splits each sitting into speech turns at the printed labels and assigns roles. Writes nuclear passages (±60 words around a keyword), dictionary frame counts and phrases. Ministerial status of plain-name turns lapses at a change of government (`GOV_STARTS`). A run-on "...Minister SHRI X (Seat):" label is read as a member's label. |
| `analyze.py` | Dictionary series by period (salience, frames, JSD, lead/lag). |
| `party.py`, `party_analysis.py` | Lok Sabha party and side labels, matched to DataMeet ECI results 1962–2004 (`GOVTS`, `HOUSES`). Rajya Sabha is not labelled (name-only matching was unreliable). |
| `sample.py`, `sample2.py` | 1962–99 coding samples: V001–V550 and W0001–W2454 (2,954 passages). |
| `sample3.py` | 2000–08 coding sample, X0001–X1493: voices ministers, LS Left / BJP / Congress / other, RS members; four periods. |
| `validate.py` | Merges and scores the 1962–99 coders (`merge` / `score` modes); Krippendorff's alpha. |
| `revoice.py` | Re-derives the voice of every coded passage from a fresh extraction (`validation/voice_fix.csv`). |
| `validated_series.py` | Main 1962–99 series from `gold.csv` + `gold2.csv`. Writes `validation/series_*.csv`; pass `broad` for all nuclear topics (`*_broad.csv`). |
| `e3.py` | 2000–08 pipeline: `merge`, `gold`, `series` → `validation/e3_*.csv`. |
| `human_check*.py` | Draw the author's check samples and compare the author's codes with the model codes. |
| `validation_gap.py` | Superseded early check on 550 passages; kept for the record. |
| `output/` | Pipeline outputs (dictionary measures, `turns.csv`, `turns_party.csv`). `passages.jsonl` (about 70 MB) is git-ignored and must be regenerated. |
| `validation/` | Codebook, samples, coder files (`codes*_claude_a/b.csv`), disagreements, adjudication rulings with reasons (`adjudication*.csv`), gold codes, series, human-check results, `REPORT.md`. |
| `validation/human_codes/` | The author's own codes exported from the coding page (`H###` = random check, `R###` = relevant-only check). |
| `PROMPTS.md` | The exact coder and adjudicator prompts used. |
| `paper/` | The paper (`closing_the_gap.md`, `.docx`), figures, `PUBLICATION.md`. |
| `tools/passage_coder.html` | Source of the human-check coding page (Claude artifact with `passages` and `codes` collections). |

## Reproduce

The three corpora are cloned side by side under one root, for example `~/corpora/`:
- `Parliamentary_Debates-Lok-Sabha-`
- `Parliamentary_Debates-Rajya-Sabha-`
- `Foreign_Affairs_Record-MEA-1955-1999`

```
cd analysis/nuclear_1962_1999
python3 extract.py ~/corpora output 1952 2008        # about 20 min on 4 cores; writes output/passages.jsonl
python3 analyze.py output
curl -o parliament.csv https://raw.githubusercontent.com/datameet/india-election-data/master/parliament-elections/parliament.csv
python3 party.py output parliament.csv
python3 party_analysis.py output
python3 -I revoice.py output validation
python3 -I validated_series.py validation output           # weapons-and-security series (main)
python3 -I validated_series.py validation output broad     # all nuclear topics
python3 -I e3.py validation series                         # 2000-08
python3 -I human_check.py validation <export_dir> human_check2_sample.csv check2 human_check2
```

The coding samples are fixed: seeds and code_ids are in `validation/`. Do not redraw them, or
the codes no longer match.

## Conventions

- Run scripts that read downloaded or corpus data with `python3 -I`.
- The repository `.gitignore` ignores `*.md`. Add Markdown files with `git add -f`.
- Never commit corpora, extracted `.md` text or `output/passages.jsonl`.
- Coder labels: `claude_a`, `claude_b`, `human_1` (the author). Never relabel model codes as human.
- Coder batches must be isolated: each coder reads only its own folder. A shared folder
  contaminated two batches once, and they had to be recoded.
- After any change to roles or parties, rerun `revoice.py` and the series, then check the
  numbers quoted in the paper.

## Status (26 October 2026)

Done:
- extraction 1952–2008;
- Lok Sabha party labels 1962–2004;
- 1962–99 validated series (weapons scope);
- 2000–08 Indo-US deal extension (H6);
- two human checks;
- the speaker-role fix;
- the paper finished through the conclusion and Appendix A.

Key results:
- MEA–members frame gap: 0.33 (1962–68) to 0.06 (1994–97).
- Ministers–members gap: small throughout.
- Keep-the-option stance: rises in the executive from 1990, then in members in 1994–97.
- 1998: splits the House (members 36 pro-bomb, 41 critical).
- 2005–08: the deal reopens the gap in position (deal-stance JSD 0.50–0.60), not in framing.

Open:
1. **Human validation of stance.** The author's stance codes agree with the model's in only 24%
   of cases (alpha 0.11). A second trained human coder on the same 30 passages (R001–R030) is the
   priority before submission.
2. **Blocked by the network policy** (allow the hosts or upload files):
   - Rajya Sabha party labels (`sansad.in`, `rajyasabha.nic.in`);
   - by-elections and the 1969 Congress split (TCPD/Lokdhaba, Wikipedia);
   - archives: Wilson Center, FRUS (`history.state.gov`), Abhilekh Patal;
   - MEA statements after 1999 (`mea.gov.in`).
3. Optional: a stance classifier over all passages (PLAN task A5); a Zenodo deposit with a DOI.
4. References were compiled from memory. Check editions and pages before submission.
