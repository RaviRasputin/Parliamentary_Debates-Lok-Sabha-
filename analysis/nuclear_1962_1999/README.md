# Executive–legislative gap on nuclear policy, 1962–1999

Start here: `CLAUDE.md` (project guide, status, how to reproduce) and `paper/closing_the_gap.md` (the paper).

Code and output tables for a paper on how far India's executive and Parliament were
apart on nuclear policy, and whether that gap narrowed between 1962 and 1999.

Sources (three companion repositories, cloned side by side under one root):

- `Parliamentary_Debates-Lok-Sabha-` and `Parliamentary_Debates-Rajya-Sabha-`: every sitting, split into speech turns
- `Foreign_Affairs_Record-MEA-1955-1999`: the MEA's diplomatic voice, in 400-word chunks

## Run

```
python3 extract.py <root containing the three repos> output 1952 2008   # 1 h or less, 4 cores; MEA stops in 1999
python3 analyze.py output
curl -o parliament.csv https://raw.githubusercontent.com/datameet/india-election-data/master/parliament-elections/parliament.csv
python3 party.py output parliament.csv      # Lok Sabha party and government/opposition labels
python3 party_analysis.py output
python3 -I revoice.py output validation        # corrected voices for the coded sample
python3 -I validated_series.py validation output   # main series (weapons and security; add 'broad' for all nuclear topics)
python3 sample.py output validation          # validation sample (550 passages)
```

`party.py` matches Lok Sabha speakers to election winners (ECI results compiled by DataMeet)
by printed constituency and an order-independent name match, then codes each member
government / outside support / opposition by the parties in office on the sitting date.
About 57% of Lok Sabha member turns are matched. Rajya Sabha speakers get a party only
from a name match against Lok Sabha winners; those labels are unreliable and are not used
in `party_analysis.py`.

`extract.py` splits each sitting at printed speaker labels, marks ministers (labels such as
"THE MINISTER OF EXTERNAL AFFAIRS (SHRI ...):" and that person's later turns), keeps turns
that mention a nuclear keyword, and codes the text within 60 words of each keyword against
seven frame dictionaries: disarmament, peaceful use, option open, discrimination,
deterrence/weapons, security threat, autonomy. An eighth column, `civil_cooperation` (civil nuclear
cooperation, 123 agreement, Hyde Act, NSG, separation plan, safeguards, fuel supply, energy security),
is reported separately for 2000–2008; `analyze.py` and `party_analysis.py` use only the seven frames
and their 1962–1999 periods. The keyword filter and phrase list also cover the 2005–08 deal
vocabulary (123 agreement, Hyde Act, civil nuclear, NSG, IAEA, separation plan, and others).
`party.py` leaves party and side empty for turns on or after 2004-05-17 (a later task).

`analyze.py` aggregates by year and period and computes the Jensen–Shannon divergence
(base 2) between ministers' and members' frame distributions, and between the MEA Record
and members, with 300-resample bootstrap intervals.

## Outputs (`output/`)

| File | Contents |
| --- | --- |
| `turns.csv` | One row per nuclear-related speech turn or MEA chunk: stable `pid` (`{house}-{date}-{n}`, MEA date = year), date, house, role, speaker, frame (7 + `civil_cooperation`) and phrase counts |
| `passages.jsonl` | One JSON object per `turns.csv` row with all its columns plus `text`, the coded window (60 words either side of each keyword) |
| `near_miss.jsonl` | Up to 20 Lok Sabha / Rajya Sabha non-chair turns per house and year with no nuclear keyword but an atom/bomb/Pokhran/fission/uranium/radioactive/reactor/test-China word (reservoir sample, seed 20261026 + year); `pid` is `NM-{house}-{date}-{n}`, `text` is 120 words around the first match. Used to check the keyword filter's recall |
| `salience_by_year.csv` | Nuclear turns and keyword hits per million words, by house and year |
| `frames_by_period.csv` | Frame shares for ministers, members and MEA, with divergences and intervals |
| `lead_lag.csv` | First year each key phrase is used (at least twice) by members, ministers and the MEA |
| `phrases_by_year.csv` | Key phrase counts by year and voice |
| `quotes.csv` | Every passage containing a key phrase, for close reading |
| `active_members.csv` | Members with the most nuclear turns, by period |
| `corpus_sizes.csv` | Words per source and year |
| `turns_party.csv` | `turns.csv` plus party, party family, match method and side |
| `gap_by_side.csv` | Divergence from the MEA and from ministers, government vs opposition benches (Lok Sabha) |
| `frames_by_family.csv` | Frame shares and key-phrase rates by party family and era (Lok Sabha) |
| `lead_lag_party.csv` | First year each phrase is used, by side and party family (Lok Sabha) |
| `robustness.csv` | Main gap measure without the security frame, and for each house separately |
| `party_coverage.csv` | Member turns by side and matched/unmatched, by period |

## Validation sample (`sample.py`, output in `validation/`)

`python3 sample.py output validation` draws, with seed 20261026, 25 passages for each of four
voices (`LS_member`, `RS_member`, `minister` = executive turns in either house, `MEA`) in each of five
eras (1962–68, 1969–79, 1980–89, 1990–97, 1998–99), i.e. 500 passages, plus 50 near-miss passages
(10 per era, voice `near_miss`) from `near_miss.jsonl`. Passages need at least 25 words, speakers labelled
"(An) Hon. Member(s)" are excluded, and text is capped at 250 words centred on the first keyword. A cell with
fewer than 25 eligible passages takes all of them and is topped up from the nearest eras; shortfalls are
printed. The 550 passages are shuffled and numbered `V001`–`V550`.

| File | Contents |
| --- | --- |
| `validation/sample.csv` | `code_id, pid, voice, era, house, date, year, speaker, role, party, side, text` |
| `validation/sample_blind.csv` | `code_id, text` only, for blind coding |
| `validation/sample_strata.csv` | Passages per voice and era (after top-ups) |

## Caveats

The text is converted from scanned pages, so words are broken and some labels misread.
Speaker roles therefore contain errors. The dictionaries are crude and need validating
against a hand-coded sample. The MEA Record yields very few nuclear passages for 1997 and 1999.
