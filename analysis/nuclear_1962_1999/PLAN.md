# Implementation plan: closing the gaps in the nuclear gap paper

Planned with Opus; written for implementing agents (Sonnet). Each task lists inputs, outputs,
method and an acceptance check. Do tasks in phase order; tasks inside a phase are independent
unless a dependency is named.

Paper: "Closing the Gap: Executive Secrecy, Parliamentary Debate and the Convergence of India's
Nuclear Position, 1962–1999" (Claude Docs artifact). Existing code in this folder:
`extract.py` (turns + frame coding), `analyze.py` (gap measures), `party.py` (Lok Sabha party
labels), `party_analysis.py` (side/family/robustness). Corpora are cloned side by side under one
root (`/home/user` in the cloud session): Lok Sabha and Rajya Sabha debate ZIPs, the MEA
Foreign Affairs Record (1955–1999) and the Selected Works of Jawaharlal Nehru (SWJN).

## Decisions by the author (26 October 2026)

- Nehru's Selected Works are dropped entirely (tasks C1 and C2 cancelled; the 1962–64 Nehru
  baseline is removed from the paper). The comparison is executive (ministers in Parliament + MEA
  Record) vs legislature (members), treated the same way for every government.
- Validation sample: 125 passages each for Lok Sabha members, Rajya Sabha members, ministers and
  the MEA Record, plus 50 near-miss passages.
- Archives: online collections only (no visits). The author will open the blocked domains
  before Phase 2.
- Agents ask the author before taking any decision this plan does not cover.

## Ground rules

- Scripts in this folder; outputs in `output/`; never commit the corpora or extracted `.md`.
- Every script takes the corpus root and output dir as arguments and runs with `python3 -I`.
- Fixed random seeds (`20261026`) wherever sampling happens.
- Anything coded by Claude is labelled `coder=claude_a` / `claude_b`; anything coded by the
  author is `coder=human_1` (a second human, if found, is `human_2`). Never relabel Claude codes as
  human codes.
- Keep the seven frames unchanged for comparability; add new variables alongside them.
- Run the fast checks before every commit: each script on a 2-year slice (e.g. 1974–1975) must
  finish without error and produce non-empty outputs.

## Environment constraints (checked 2026-10-26)

Reachable: `raw.githubusercontent.com`, `pypi.org`. Blocked: `en.wikipedia.org`, `sansad.in`,
`rajyasabha.nic.in`, `loksabha.nic.in`, `lokdhaba.ashoka.edu.in`, `eci.gov.in`, `mea.gov.in`,
`digitalarchive.wilsoncenter.org`, `abhilekh-patal.in`, `huggingface.co`. Tasks that need a blocked
host say so and have a fallback (author uploads files). `pip install scikit-learn` works.

---

## Phase 1 — data preparation (no author input needed)

### A1. Save passage text and draw the validation sample

- Change `extract.py` so it also writes `output/passages.jsonl`: one record per row of
  `turns.csv` with a stable `pid` (`{house}-{date}-{n}`), all existing columns, and the coded
  window text `text`. Add the same `pid` column to `turns.csv`.
- Re-run extraction for 1952–2008 in one pass (feeds A1, C3 and E1). Expect ~60 min on 4 cores.
- `sample.py`: draw 500 passages stratified by voice × era.
  - Voices: LS members, RS members, ministers (both houses), MEA.
  - Eras: 1962–68, 1969–79, 1980–89, 1990–97, 1998–99.
  - Allocation: 125 per voice, 25 per era; where a cell is short, take all and top up from
    the adjacent era of the same voice.
  - Drop passages under 25 words; cap text at 250 words around the keyword.
  - Add 50 "near-miss" passages: turns with no nuclear keyword but containing "atom", "bomb",
    "Pokhran" misspellings or "test" + "China", to estimate the keyword filter's recall.
- Outputs: `validation/sample.csv` (pid, voice, era, house, date, speaker, role, party, side,
  text) and `validation/sample_blind.csv` (pid, text only — no dictionary codes, no speaker
  role, so coders are blind to them).
- Accept: 550 rows, no duplicate pids, strata counts printed and match the allocation.

### A2. Codebook (Opus drafts, author approves)

`validation/CODEBOOK.md`. For each passage, coders record:

1. `relevant` — is the passage about nuclear weapons, nuclear energy or nuclear diplomacy?
   (yes / no). If no, stop.
2. Seven frames, each present/absent (multi-label), with definitions, inclusion and exclusion
   rules and two corpus examples each: disarmament, peaceful_use, option_open, discrimination,
   deterrence_weapon, security_threat, autonomy.
3. `stance` on India's own nuclear posture (single label):
   `pro_bomb` (India should build/test/weaponise), `keep_option` (retain capability and freedom,
   neither renounce nor build now), `disarmament` (India should renounce or press global
   disarmament as the answer), `peaceful_only` (nuclear energy for development, weapons not
   discussed), `critical_of_tests` (after 1974/1998: opposes the act or its timing), `neutral`
   (procedural, factual, question without position), `other_country` (about another state's
   programme only).
4. `confidence` 1–3.

Pilot: both Claude coders and the author code the same 30 passages; Opus revises the codebook
where they disagree; then freeze it (version tag in the file).

### C1. Split Nehru's Selected Works into documents — CANCELLED (author decision)

- `swjn_docs.py`: for each Second Series volume (1–85, including part files), parse the table
  of contents. Entries look like `9. In New Delhi: Press Conference 31/12/62 8` — number, title,
  date (dd/mm/yy), printed page. Locate each document's start in the body by matching its title
  after the `### [PDF p. N]` marker nearest the printed page offset (estimate the offset per
  volume from the first three matches). The document runs to the next document's start.
- Strip editorial matter: lines starting with a footnote number followed by a short reference
  (heuristic: `^\d{1,3}\.? ` within the last 30% of a page and under 300 characters), section
  headings in capitals, and running heads.
- Classify `doc_type` from the title:
  - `public`: "In the Lok Sabha", "In the Rajya Sabha", "Speech", "Press Conference",
    "Broadcast", "Message" (published), "Interview", "Statement", "In <place>:" (public address).
  - `cm_letter`: "To Chief Ministers" (fortnightly letters; semi-official, analysed separately).
  - `private`: "To <person>" letters, "Note", "Cable", "Minutes", "Telegram", "Record of talk".
  - `unknown`: anything else.
- Outputs: `output/swjn_documents.csv` (volume, doc_no, title, date, doc_type, n_words,
  start_page) and `output/swjn_documents.jsonl` with text.
- Accept: ≥90% of TOC entries located; `unknown` ≤10%; author spot-checks 50 random documents
  (title, type and boundaries) — record results in `validation/swjn_check.csv`.

### E1. Extend extraction to 1952–2008 (same run as A1)

- `extract.py` already handles any year range; extend `NUC` and `PHRASES` with: "123
  agreement", "Hyde Act", "civil nuclear (cooperation|deal|agreement)", "NSG", "Nuclear
  Suppliers Group", "separation plan", "IAEA safeguards", "moratorium", "strategic autonomy",
  "credible minimum deterrence". Do not change the seven frame dictionaries; add an eighth
  column `civil_cooperation` (civil nuclear cooperation, 123, Hyde, NSG, separation plan,
  safeguards, fuel supply, energy security) reported separately.
- The MEA Record in this repo stops in 1999. See E2 for the executive voice after 1999.
- Accept: `turns.csv` covers 1952–2008; spot-check 20 passages from 2005–2008 contain deal
  vocabulary.

---

## Phase 2 — coding and data that need the author

### A3. Code the validation sample

- Claude coder A and Claude coder B: two independent Sonnet subagents, each coding
  `sample_blind.csv` in batches of 50 with the frozen codebook. Coder B sees passages in a
  different random order. Output `validation/codes_claude_a.csv`, `codes_claude_b.csv`
  (pid, relevant, 7 frames, stance, confidence, one-line rationale).
- Author coding: 150 passages (30 per voice), via a coding page built as a Claude artifact
  with a shared database (one passage per screen, checkboxes for frames, radio buttons for
  stance, keyboard shortcuts; saves each answer). Export to `validation/codes_human_1.csv`.
  If a second person (colleague or RA) can code the same 150, store as `codes_human_2.csv`.
- Accept: all 550 coded by both Claude coders; ≥150 by the author.

### B1. Rajya Sabha party labels

Needs one of: `sansad.in` / `rajyasabha.nic.in` / `en.wikipedia.org` allowed, or the author
uploads the Rajya Sabha Secretariat's list of members since 1952 (name, state, party, term
start/end).
- `rs_party.py`: build `output/rs_members.csv` (name tokens, state, party, term_start,
  term_end). Match RS speaker labels using the printed state in the label plus the
  order-independent name matcher from `party.py`, constrained to members whose term covers the
  sitting date.
- Accept: ≥70% of RS member turns matched; author checks 100 random matches, ≥95% correct.

### B2. Lok Sabha by-elections and party switches

- By-elections: needs Lokdhaba/TCPD data or Wikipedia (blocked); fallback is author upload of
  TCPD's Lok Sabha file (includes by-elections). Add winners with their own term dates.
- 1969 Congress split: build `data/switches.csv` (name, from_party, to_party, date,
  source) for Lok Sabha members who joined Congress (O) in November 1969, from a cited list
  (e.g. Lok Sabha party position statements or a published list; author to confirm source).
  Also record other documented switches in 1962–2008 where a source is available. `party.py`
  applies a switch from its date onward.
- Accept: re-run `party.py`; LS coverage ≥75%; 1969–71 government/opposition split reflects
  Congress (O) as opposition.

### D1. Archival collection (online only)

Claude searches the online collections once the domains are open, proposes documents, and the
author approves what goes in; Claude registers and codes them. Indian private papers (e.g. the
P. N. Haksar papers) are not online and are out of scope.
- Targets, by window:
  - 1964–68 (China's test, NPT): digitised MEA/PMO files on Abhilekh Patal; Wilson Center
    NPIHP India collection; FRUS 1964–68 vol. XXV (South Asia).
  - 1972–74 (PNE decision): Abhilekh Patal; Wilson Center; FRUS 1969–76 vol. E-8 (South Asia
    1973–76).
  - 1995–98: limited declassification — use memoirs (Jaswant Singh, Strobe Talbott),
    published interviews, and the 1998 government papers tabled in Parliament.
- Uploads go to `archive/raw/` (PDFs or photos). `archive_register.py` OCRs them (pytesseract
  if installable, otherwise the author supplies text) and writes `archive/register.csv`:
  doc_id, source, file_no, date, author, recipient, classification, title, n_words, text_path.
- Claude codes each archival document with the frozen codebook (frames + stance) as the
  "private executive" voice.
- Accept: ≥100 registered documents across the three windows, each with a source citation.

### E2. Executive voice after 1999

Needs `mea.gov.in` allowed (Foreign Affairs Record / speeches and statements archive) or author
uploads. Fallback: use ministers' statements in Parliament plus PM/EAM suo motu statements as the
executive voice for 2000–08, and flag the change of source in the paper.

---

## Phase 3 — analysis

### A4. Validate the dictionaries

- `validate.py`: agreement and accuracy.
  - Krippendorff's alpha (nominal) for `relevant`, each frame, and `stance`, for every coder
    pair: human_1–claude_a, human_1–claude_b, claude_a–claude_b (and human_1–human_2 if present).
    Implement alpha directly (no extra dependency) and unit-test it on a textbook example.
  - Gold labels: human_1 where available; elsewhere the Claude A/B consensus, with
    disagreements adjudicated by Opus and marked `adjudicated=1`.
  - Dictionary performance per frame against gold: precision, recall, F1 (dictionary "present"
    = frame count ≥1 in the passage window).
  - Keyword filter recall from the 50 near-miss passages.
- Revise dictionaries only where the confusion is clear (e.g. "club", "pressure",
  "options open"); keep the old version, re-run the main gap measures with both, and report
  both.
- Outputs: `validation/agreement.csv`, `validation/dictionary_performance.csv`,
  `validation/REPORT.md`.
- Accept: report states alphas and F1s with confidence intervals; any frame with F1 < 0.6 is
  flagged in the paper.

### A5. Stance classifier

- Training data: the 550 validation passages plus 1,500 more passages drawn the same way and
  coded by Claude A (spot-checked by the author: 100 of them).
- Models: (1) TF-IDF (word 1–2-grams, character 3–5-grams for OCR noise) + logistic regression,
  class-weighted; (2) the same with the seven frame counts as extra features. scikit-learn.
- Evaluation: 5-fold CV on the training set; final test on the human-coded 150 only. Report
  macro-F1, per-class F1 and confusion matrix.
- Apply the best model to every passage 1952–2008 (`turns_stance.csv`).
- New measures: stance shares by voice, side and party family per period; stance-based JSD
  between voices (same bootstrap as the frame JSD).
- Accept: macro-F1 ≥ 0.65 on the human test set; if lower, report it and use stance only
  descriptively.

### C2. Nehru's private–public gap — CANCELLED (author decision)

- Code `swjn_documents.jsonl` windows with the frame dictionaries (and the stance classifier
  from A5).
- Measures by year 1947–1964: JSD between private, public and CM letters; each vs Parliament
  members of the same year (from the 1952–2008 extraction); salience by type.
- Accept: table and chart of the three Nehru voices against members; ≥50 nuclear documents per
  type for the years reported, else pooled periods.

### D2. Private-executive voice

- Add archival documents as a fourth voice in `analyze.py` for the three windows; compute
  private-executive vs members, vs ministers and vs MEA.
- Qualitative: for each window, a short process-tracing note pairing archival documents with
  the debates of the same weeks (`archive/notes/<window>.md`).

### E3. The Indo-US deal, 2005–2008

DONE (26 October 2026, author chose a model-coded sample over dictionaries): `sample3.py`, `e3.py`,
codebook 1.2 section 7; results in `validation/REPORT.md` and paper section 5.8 (H6).

- Periods: NDA to May 2004; UPA-I May 2004 – July 2008 with Left outside support; after the
  Left's withdrawal (8 July 2008) and the trust vote (22 July 2008).
- Party labels from DataMeet's 2004 results; government sets: NDA (BJP + allies) to 22 May
  2004; UPA (INC + allies) after, with CPI(M), CPI, RSP, FB as outside support until 8 July 2008.
- Measures: gap between ministers/executive voice and (a) the Left, (b) the BJP, (c) Congress
  backbenchers, 1999–2008; use of "strategic autonomy", "Hyde Act", "123", "moratorium",
  "testing" by family.
- Hypothesis H7: the deal reopened the gap, with the Left (sovereignty, US) and the BJP
  (testing rights, autonomy) diverging from the executive for different reasons.

---

## Phase 4 — integration and review

- Opus reviews every output adversarially (wrong denominators, thin cells, leakage between
  training and test sets, mislabelled coders), then updates the paper: methods (codebook,
  validation statistics), results (stance, party, Nehru, 2005–08), limitations, appendix tables.
- Archive code + derived data on Zenodo with a DOI before submission.

## Model assignment

| Work | Model |
| --- | --- |
| Codebook design, adjudication, review, paper writing | Opus |
| Scripts (A1, E1, B1, B2, A4, A5, D2, E3), batch coding (Claude A/B) | Sonnet |
| Gold-standard coding, approving archive documents and sources, opening domains | Author |
