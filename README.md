# Lok Sabha Debates — Markdown Archive (1952–2026)

A plain-text archive of the official **Lok Sabha** (House of the People) debates of the Parliament of India, covering the First Lok Sabha (1952) through 2026. The debates are published by Parliament only as scanned PDFs, which are hard to search and analyse at scale. This repository repackages them as searchable **Markdown**, with **one file per calendar year**, compiled from **6,871 source PDFs**.

The data lives in [`data/`](data/) as one ZIP per year — `data/1952.zip` … `data/2026.zip`. Each ZIP contains a single `<year>.md`.

| | |
|---|---|
| **Years covered** | 1952–2026 (75 years) |
| **Source PDFs compiled** | 6,871 |
| **Uncompressed text** | ~4.2 GB |
| **Compressed (in repo)** | ~1.4 GB |
| **Format** | UTF-8 Markdown, one file per year, zipped |

---

## Repository layout

```
.
├── README.md            # this file
├── LICENSE              # licensing for the code in this repo
├── manifest.csv         # per-year stats: source PDF count, raw size, zip size, ratio
├── .gitignore
├── data/                # the archive — one ZIP per year
│   ├── 1952.zip         #   └─ contains 1952.md
│   ├── 1953.zip
│   ├── ...
│   └── 2026.zip
└── scripts/             # reference implementation of the build pipeline
    ├── 1_download_pdfs.py
    ├── 2_arrange_by_year.py
    └── 3_compile_to_markdown.py
```

The year files are stored as ZIPs because several exceed GitHub's 100 MB per-file limit when uncompressed (e.g. 2025 is ~138 MB of text). Zipping keeps every file well under the limit (largest is ~44 MB) and the OCR text compresses ~3.3×.

## Coverage by decade

| Decade | Years | Source PDFs | Compressed size |
|---|---:|---:|---:|
| 1950s | 8  | 1,021 | 141 MB |
| 1960s | 10 | 1,169 | 219 MB |
| 1970s | 10 | 1,000 | 216 MB |
| 1980s | 10 | 959   | 231 MB |
| 1990s | 10 | 763   | 160 MB |
| 2000s | 10 | 716   | 168 MB |
| 2010s | 10 | 901   | 144 MB |
| 2020s | 7  | 342   | 91 MB  |

Full per-year figures are in [`manifest.csv`](manifest.csv). Coverage reflects what was available in the source archive at the time of download; sitting days, and therefore PDF counts, vary year to year (election years and short sessions have fewer).

---

## How this archive was built

The archive was produced by a scripted pipeline in three stages: **download → arrange by year → convert to Markdown.** Reference implementations of each stage are in [`scripts/`](scripts/).

### 1. Downloading the source PDFs

The debate PDFs were **downloaded in bulk by a script** from the official Parliament of India debate archive (Digital Sansad / the Parliament Digital Library, which host the Lok Sabha Debates). The script walks the archive's listing of Lok Sabha debate volumes and downloads each sitting's PDF, preserving the original filenames.

Source filenames follow Parliament's own convention, e.g. `lsd_01_01_13-05-1952.pdf`:

```
lsd _ 01 _ 01 _ 13-05-1952 .pdf
 │    │    │     └ sitting date (DD-MM-YYYY)
 │    │    └ debate / part number
 │    └ Lok Sabha number (01 = First Lok Sabha)
 └ "Lok Sabha Debates"
```

Because the sitting date is embedded in every filename, downloads can be verified and re-run idempotently (skip files already fetched).

### 2. Arranging year-wise

Each PDF was assigned to a calendar year using the **date in its filename**, then grouped into per-year sets. This is the organising key for the whole archive: everything that happened in sittings during a given year is collected together, regardless of which session or volume it came from. Within a year, PDFs are ordered chronologically by sitting date.

### 3. Converting to Markdown

The source PDFs are **scanned images**, so each was passed through **OCR** (optical character recognition, e.g. Tesseract via OCRmyPDF / `pdftotext` for text-layer PDFs) to extract its text. For each year, the extracted text of every PDF was then concatenated into a single `<year>.md` file with:

- a top header — `# Lok Sabha Debates — <year>` — and a provenance line recording how many source PDFs were compiled and when the file was generated;
- one section per source PDF, introduced by a heading that carries the **sitting date and original filename**, so any passage can be traced back to its source document.

```markdown
# Lok Sabha Debates — 1952

_Compiled from 103 source PDF(s). Generated 2026-06-17._

---

## 1952-05-13 — lsd_01_01_13-05-1952.pdf

<OCR text of that sitting's debate…>

## 1952-05-14 — lsd_01_01_14-05-1952.pdf

<…>
```

This layout keeps each year as one self-contained, greppable document while preserving a clear trail back to the exact PDF every line came from.

---

## Using the data

Unzip a single year:

```bash
unzip data/1952.zip          # → 1952.md
```

Unzip everything:

```bash
cd data && for z in *.zip; do unzip -o "$z"; done
```

Search across years without unzipping to disk (example with `ripgrep`):

```bash
for z in data/*.zip; do
  unzip -p "$z" | rg -i "five year plan" | sed "s|^|$(basename "$z" .zip): |"
done
```

Each `<year>.md` is plain UTF-8 Markdown, so it works with any text editor, `grep`/`ripgrep`, pandas, or an LLM ingestion pipeline.

## Reproducing the pipeline

The scripts in [`scripts/`](scripts/) are a **reference implementation** of the download → arrange → compile pipeline described above. They document the method and let others rebuild or extend the archive; adapt the source URLs and OCR settings to your environment before running.

```bash
pip install requests ocrmypdf pytesseract pypdf   # plus the Tesseract binary
python scripts/1_download_pdfs.py   --out pdfs/
python scripts/2_arrange_by_year.py --in pdfs/ --out by_year/
python scripts/3_compile_to_markdown.py --in by_year/ --out markdown/
```

## Data quality & limitations

- **OCR errors.** The text is machine-recognised from decades-old scans. Older volumes (1950s–1970s) in particular contain recognition errors, broken words, stray characters, and imperfect spacing. Treat the text as a search-and-research aid, not a verbatim certified transcript.
- **Layout loss.** Original column layouts, tables, and marginal column-numbers are flattened into linear text.
- **Source completeness.** The archive contains what was published and available for download; if Parliament's archive was missing a sitting, it is missing here too.
- **Authoritative copy.** For citation or legal use, always refer back to the original PDF named in the relevant section heading.

## Source & attribution

The underlying debates are official records of the **Lok Sabha, Parliament of India**, retrieved from Parliament's public digital archives. All proceedings are public records of the Government of India. This repository only reformats them; it does not alter their content beyond OCR text extraction.

## License

The debate **content** consists of Government of India parliamentary records and is reproduced here for research and public access; rights in the original material rest with their respective owners. The **code** in this repository (the pipeline in `scripts/`) is released under the MIT License — see [`LICENSE`](LICENSE).
