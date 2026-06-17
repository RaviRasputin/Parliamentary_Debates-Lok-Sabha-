#!/usr/bin/env python3
"""
Stage 1 — Download the Lok Sabha debate PDFs.

Reference implementation of the bulk download step. It fetches the official
Lok Sabha Debates PDFs from Parliament's public digital archive and saves them
with their original filenames (e.g. ``lsd_01_01_13-05-1952.pdf``). The run is
idempotent: files already present (with a non-zero size) are skipped, so an
interrupted download can simply be re-run.

NOTE: plug your archive's listing into ``iter_pdf_urls()``. The official
sources are Digital Sansad (https://sansad.in) and the Parliament Digital
Library (https://eparlib.nic.in), which expose the Lok Sabha Debates volumes.

    python scripts/1_download_pdfs.py --out pdfs/
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Iterator

import requests

USER_AGENT = "lok-sabha-debates-archiver/1.0 (+research; contact: you@example.com)"
REQUEST_TIMEOUT = 60
RETRIES = 3
PAUSE_SECONDS = 1.0  # be polite to the source server


def iter_pdf_urls() -> Iterator[tuple[str, str]]:
    """Yield ``(filename, url)`` pairs for every debate PDF to download.

    Replace the body with the enumeration logic for your source. Typically you
    would page through the archive's volume/sitting listing and read each PDF
    link. Filenames should be preserved exactly so the date they encode can be
    parsed later in stage 2.
    """
    raise NotImplementedError(
        "Provide the listing for your source archive here. Each item must be a "
        "(filename, url) tuple, e.g. ('lsd_01_01_13-05-1952.pdf', 'https://.../...pdf')."
    )


def download_one(url: str, dest: Path, session: requests.Session) -> bool:
    for attempt in range(1, RETRIES + 1):
        try:
            with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 16):
                        fh.write(chunk)
                tmp.replace(dest)  # atomic on the same filesystem
            return True
        except Exception as exc:  # noqa: BLE001 - reference script
            print(f"  attempt {attempt}/{RETRIES} failed for {url}: {exc}")
            time.sleep(2 * attempt)
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Download Lok Sabha debate PDFs.")
    ap.add_argument("--out", type=Path, default=Path("pdfs"), help="output directory")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    ok = skipped = failed = 0
    for filename, url in iter_pdf_urls():
        dest = args.out / filename
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        print(f"downloading {filename}")
        if download_one(url, dest, session):
            ok += 1
        else:
            failed += 1
        time.sleep(PAUSE_SECONDS)

    print(f"\nDone. downloaded={ok} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
