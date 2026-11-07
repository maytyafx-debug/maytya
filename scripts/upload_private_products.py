"""Upload paid PRO deliverables to the existing private Supabase Storage bucket."""
import os
from pathlib import Path
import requests

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
        if len(check.content) != path.stat().st_size:
            raise SystemExit(f"Verification size mismatch for {name}")
        print(f"PRIVATE_OK {name}: {len(check.content)} bytes")

    print(f"PRIVATE_PRODUCTS_OK={len(FILES)}")

if __name__ == "__main__":
    main()
