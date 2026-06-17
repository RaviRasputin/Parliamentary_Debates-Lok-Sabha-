#!/usr/bin/env python3
"""
Stage 3 — Convert the per-year PDFs into one Markdown file per year.

For each year folder produced by stage 2 this script extracts the text of
every PDF and concatenates it into a single ``<year>.md``. PDFs with a real
text layer are read directly; scanned (image-only) PDFs are passed through OCR.

Output format (matches the files shipped in this repository):

    # Lok Sabha Debates — <year>

    _Compiled from <N> source PDF(s). Generated <YYYY-MM-DD>._

    ---

    ## <YYYY-MM-DD> — <filename>

    <text of that sitting>

    ## <YYYY-MM-DD> — <filename>
    ...

    python scripts/3_compile_to_markdown.py --in by_year/ --out markdown/

OCR backends (optional, used only when a PDF has no text layer):
    pip install pypdf ocrmypdf pytesseract pdf2image   # + the Tesseract binary
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import tempfile
from pathlib import Path

DATE_RE = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
MIN_TEXT_CHARS = 200  # below this we assume the PDF is scanned and needs OCR


def sitting_date(filename: str) -> str:
    m = DATE_RE.search(filename)
    if not m:
        return "0000-00-00"
    d, mo, y = m.groups()
    return f"{y}-{mo}-{d}"


def text_layer(pdf: Path) -> str:
    """Extract an existing text layer, if any (no OCR)."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception:
        return ""


def ocr(pdf: Path) -> str:
    """OCR a scanned PDF to text. Tries ocrmypdf, then pdf2image+pytesseract."""
    # Preferred: ocrmypdf adds a text layer, then we read it back.
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            out = Path(tmp.name)
        subprocess.run(
            ["ocrmypdf", "--force-ocr", "--quiet", str(pdf), str(out)],
            check=True,
        )
        text = text_layer(out)
        out.unlink(missing_ok=True)
        if text:
            return text
    except Exception:
        pass
    # Fallback: rasterise pages and OCR each with Tesseract.
    try:
        import pytesseract
        from pdf2image import convert_from_path

        pages = convert_from_path(str(pdf), dpi=300)
        return "\n".join(pytesseract.image_to_string(p, lang="eng") for p in pages).strip()
    except Exception as exc:  # noqa: BLE001 - reference script
        print(f"    OCR failed for {pdf.name}: {exc}")
        return ""


def extract(pdf: Path) -> str:
    text = text_layer(pdf)
    if len(text) >= MIN_TEXT_CHARS:
        return text
    return ocr(pdf)


def compile_year(year_dir: Path, out_dir: Path) -> None:
    year = year_dir.name
    pdfs = sorted(year_dir.glob("*.pdf"), key=lambda p: sitting_date(p.name))
    if not pdfs:
        return

    today = dt.date.today().isoformat()
    parts = [
        f"# Lok Sabha Debates — {year}",
        "",
        f"_Compiled from {len(pdfs)} source PDF(s). Generated {today}._",
        "",
        "---",
        "",
    ]
    for pdf in pdfs:
        print(f"  {year}: {pdf.name}")
        parts.append(f"## {sitting_date(pdf.name)} — {pdf.name}")
        parts.append("")
        parts.append(extract(pdf))
        parts.append("")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{year}.md").write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compile per-year PDFs into Markdown.")
    ap.add_argument("--in", dest="src", type=Path, default=Path("by_year"))
    ap.add_argument("--out", dest="dst", type=Path, default=Path("markdown"))
    args = ap.parse_args()

    for year_dir in sorted(d for d in args.src.iterdir() if d.is_dir()):
        compile_year(year_dir, args.dst)

    print(f"\nDone. Markdown written to {args.dst}/")


if __name__ == "__main__":
    main()
