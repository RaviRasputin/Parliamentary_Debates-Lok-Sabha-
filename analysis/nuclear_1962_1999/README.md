# Executive–legislative gap on nuclear policy, 1962–1999

Code and output tables for a paper on how far India's executive and Parliament were
apart on nuclear policy, and whether that gap narrowed between 1962 and 1999.

Sources (all four companion repositories, cloned side by side under one root):

- `Parliamentary_Debates-Lok-Sabha-` and `Parliamentary_Debates-Rajya-Sabha-`: every sitting, split into speech turns
- `Foreign_Affairs_Record-MEA-1955-1999`: the MEA's diplomatic voice, in 400-word chunks
- `Selected_Works_of_JLN`: Second Series Vols. 75–85 (Feb 1962 – May 1964)

## Run

```
python3 extract.py <root containing the four repos> output 1962 1999   # ~30 min, 4 cores
python3 analyze.py output
curl -o parliament.csv https://raw.githubusercontent.com/datameet/india-election-data/master/parliament-elections/parliament.csv
python3 party.py output parliament.csv      # Lok Sabha party and government/opposition labels
python3 party_analysis.py output
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
deterrence/weapons, security threat, autonomy.

`analyze.py` aggregates by year and period and computes the Jensen–Shannon divergence
(base 2) between ministers' and members' frame distributions, and between the MEA Record
and members, with 300-resample bootstrap intervals.

## Outputs (`output/`)

| File | Contents |
| --- | --- |
| `turns.csv` | One row per nuclear-related speech turn or MEA/SWJN chunk: date, house, role, speaker, frame and phrase counts |
| `salience_by_year.csv` | Nuclear turns and keyword hits per million words, by house and year |
| `frames_by_period.csv` | Frame shares for ministers, members and MEA, with divergences and intervals |
| `lead_lag.csv` | First year each key phrase is used (at least twice) by members, ministers and the MEA |
| `phrases_by_year.csv` | Key phrase counts by year and voice |
| `quotes.csv` | Every passage containing a key phrase, for close reading |
| `active_members.csv` | Members with the most nuclear turns, by period |
| `nehru_baseline.json` | Frame shares in Nehru's Selected Works, 1962–64 |
| `corpus_sizes.csv` | Words per source and year |
| `turns_party.csv` | `turns.csv` plus party, party family, match method and side |
| `gap_by_side.csv` | Divergence from the MEA and from ministers, government vs opposition benches (Lok Sabha) |
| `frames_by_family.csv` | Frame shares and key-phrase rates by party family and era (Lok Sabha) |
| `lead_lag_party.csv` | First year each phrase is used, by side and party family (Lok Sabha) |
| `robustness.csv` | Main gap measure without the security frame, and for each house separately |
| `party_coverage.csv` | Member turns by side and matched/unmatched, by period |

## Caveats

The text is converted from scanned pages, so words are broken and some labels misread.
Speaker roles therefore contain errors. The dictionaries are crude and need validating
against a hand-coded sample. The MEA Record yields very few nuclear passages for 1997 and 1999.
