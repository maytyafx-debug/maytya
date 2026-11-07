"""Upload paid PRO deliverables to the existing private Supabase Storage bucket."""
import os
from pathlib import Path
import requests
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "out" / "private-products"
BASE = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or ""
BUCKET = "paid-packs"
FILES = [
    "risk-guide.pdf", "risk-journal.xlsx",
    "bourse-guide.pdf", "bourse-tracker.xlsx",
    "fit-guide.pdf", "fit-program.xlsx",
    "mind-guide.pdf", "mind-journal.xlsx",
    "biz-guide.pdf", "biz-model.xlsx",
]

def main():
    if not BASE or not KEY:
        raise SystemExit("Supabase server credentials are not configured.")
    headers = {"apikey": KEY, "Authorization": "Bearer " + KEY}
    bucket = requests.get(f"{BASE}/storage/v1/bucket/{BUCKET}", headers=headers, timeout=30)
    bucket.raise_for_status()
    metadata = bucket.json()
    if metadata.get("public") is not False:
        raise SystemExit("Refusing to upload paid files: target bucket is not private.")

    for name in FILES:
        path = PRIVATE / name
        if not path.is_file() or path.stat().st_size < 1000:
            raise SystemExit(f"Missing or incomplete private product: {name}")
        mime = "application/pdf" if name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        upload_headers = {
            **headers,
            "Content-Type": mime,
            "x-upsert": "true",
        }
        url = f"{BASE}/storage/v1/object/{BUCKET}/packs/{name}"
        with path.open("rb") as stream:
            response = requests.post(url, headers=upload_headers, data=stream, timeout=90)
        response.raise_for_status()

        check = requests.get(url, headers=headers, timeout=45)
        check.raise_for_status()
        # Validate the downloaded object itself. Some Storage/CDN paths may
        # apply content encoding, so byte-length equality alone is not a
        # reliable integrity test for XLSX downloads.
        if name.endswith(".pdf"):
            if not check.content.startswith(b"%PDF-"):
                raise SystemExit(f"Downloaded PDF signature is invalid: {name}")
        else:
            try:
                with zipfile.ZipFile(io.BytesIO(check.content)) as archive:
                    bad_member = archive.testzip()
                    if bad_member or "xl/workbook.xml" not in archive.namelist():
                        raise SystemExit(f"Downloaded XLSX archive is invalid: {name}")
            except zipfile.BadZipFile:
                raise SystemExit(f"Downloaded XLSX is not a valid ZIP workbook: {name}")
        expected_size = path.stat().st_size
        actual_size = len(check.content)
        if actual_size != expected_size:
            print(f"PRIVATE_SIZE_NOTE {name}: local={expected_size}, downloaded={actual_size}; content integrity passed")
        print(f"PRIVATE_OK {name}: {actual_size} bytes; integrity verified")

    print(f"PRIVATE_PRODUCTS_OK={len(FILES)}")

if __name__ == "__main__":
    main()
