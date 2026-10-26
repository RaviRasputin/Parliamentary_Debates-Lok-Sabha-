# Coding prompts

These are the prompts used to code the samples with Claude, for replication. Each coder ran as a
separate Claude Code subagent (Sonnet) in its own folder. The folder held only `CODEBOOK.md` and
`batch.csv` (code_id, text): no speaker, date, party or source. Adjudicators ran as Opus
subagents.

## Coder (2000–08 sample, codebook 1.2)

The 1962–99 samples used the same prompt under codebook 1.0, without `deal_stance` and with
relevance as defined in that version. Each batch (about 187 passages) was coded once by
`claude_a` and once by `claude_b`.

```
You are coder claude_a coding passages from Indian parliamentary debates, 2000-2008, for a
research project. Work ONLY inside the folder <batch folder>. Do not open, list or read any
other folder or file anywhere else (no other iso_* folders, no repositories, no metadata). Do
not look up speakers or dates.

1. Read CODEBOOK.md in that folder in full. Sections 1-5 and section 7 (the 2000-2008 addendum,
   version 1.2) apply. Relevance follows section 1 as amended by section 7: weapons and security
   topics, plus any passage about the Indo-US civil nuclear deal.
2. Read batch.csv (columns code_id, text). Code every passage yourself by reading it: no keyword
   scripts, no automated classification. Text is OCR'd and may be noisy or in Hindi; read
   through it.
3. Write codes.csv in the same folder with exactly these columns in this order:
   code_id,coder,relevant,disarmament,peaceful_use,option_open,discrimination,deterrence_weapon,
   security_threat,autonomy,stance,deal_stance,confidence,note
   - coder = claude_a
   - relevant = yes/no
   - frames 1/0 (all 0 when relevant=no)
   - stance one of pro_bomb, keep_option, disarmament, critical_of_tests, peaceful_only,
     other_country, neutral (empty when relevant=no)
   - deal_stance one of support, oppose, conditional, neutral, none (empty when relevant=no)
   - confidence 1/2/3; note under 20 words (required when confidence is 1). Quote any field
     that contains a comma. Every row must have exactly 14 fields, including not-relevant rows.
4. One row per passage, every code_id in batch.csv exactly once. Check the row count and the
   field count with a short script at the end and fix any problem.
```

## Adjudicator

The folder held `CODEBOOK.md`, `disagreements.csv` (code_id, fields in dispute, text, both
coders' codes as JSON) and earlier rulings as precedent.

```
You are the adjudicator for a content-analysis study of Indian parliamentary debates. Work only
in <folder> and read no other folder.

- CODEBOOK.md: the codebook (sections 1-5, and section 7 for 2000-08).
- disagreements.csv: passages on which two blind coders (a, b) disagreed.
- precedent csv: earlier rulings. Read it for consistency of interpretation; follow it where it
  applies.

For each passage, read the text and decide every field listed in `fields`, applying the
codebook strictly. You may choose a value neither coder chose. If you rule relevant=no, write
that one row only. If you rule relevant=yes on a relevance dispute, also rule on all frames,
stance (and deal_stance), because these were never jointly coded.

Write adjudication.csv with columns code_id,field,value,reason: one row per field ruled.
Reasons are under 25 words and cite the text or a codebook rule. Check with a short script that
every disputed field of every passage has a row.
```

Rulings are in `validation/adjudication.csv`, `adjudication2.csv` and `adjudication3.csv`.
Gold codes take a field from the adjudication where one exists, and otherwise from the two
coders' agreed value.
