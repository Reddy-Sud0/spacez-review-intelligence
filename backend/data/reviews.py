"""
Loads all 46 reviews from the Excel dataset at runtime.
Path: spacez_reviews_dataset.xlsx (one level above backend/)

Column mapping from Excel → review dict:
  review_id      → id
  platform       → platform
  property_id    → property_id
  property_name  → property_name
  location       → location
  caretaker_id   → caretaker_id
  caretaker_name → caretaker_name
  rating_raw     → rating_raw  (float)
  rating_scale   → rating_scale (int)
  host_responded → host_responded (bool: "Yes"→True, "No"→False)
  guest_name     → guest_name
  review_text    → review_text

Special flags (not in Excel — applied by business rules):
  noise_flag    → RV035 (policy_complaint), RV041 (too_vague)
  resolved_flag → RV036 (pool_fixed)
"""

import openpyxl
from pathlib import Path
from typing import List, Dict, Any

# Excel can be at project root (local dev) or beside backend/ (Render)
_here = Path(__file__).parent          # backend/data/
_candidates = [
    _here.parent.parent / "spacez_reviews_dataset.xlsx",   # local: spacez/
    _here.parent.parent.parent / "spacez_reviews_dataset.xlsx",  # one more up
    _here.parent / "spacez_reviews_dataset.xlsx",           # inside backend/
    Path("spacez_reviews_dataset.xlsx"),                    # cwd (Render root)
]
EXCEL_PATH = next((p for p in _candidates if p.exists()), _candidates[0])

# Special flags that override or annotate specific reviews (business rules)
NOISE_FLAGS: Dict[str, str] = {
    "RV035": "policy_complaint",
    "RV041": "too_vague",
}

RESOLVED_FLAGS_EXCEL: Dict[str, str] = {
    "RV036": "pool_fixed",
}


def _load_reviews_from_excel() -> List[Dict[str, Any]]:
    """Parse the Excel file and return a list of review dicts."""
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"Excel dataset not found at: {EXCEL_PATH}\n"
            "Make sure 'spacez_reviews_dataset.xlsx' is in the project root (spacez/)."
        )

    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)

    # The review data is in the first sheet ("Reviews")
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))

    if not rows:
        raise ValueError("Excel sheet is empty.")

    headers = [str(h).strip() if h else "" for h in rows[0]]

    def idx(col: str) -> int:
        return headers.index(col)

    reviews: List[Dict[str, Any]] = []
    for row in rows[1:]:
        if row[idx("review_id")] is None:
            continue  # skip blank trailing rows

        review_id  = str(row[idx("review_id")]).strip()
        host_resp  = str(row[idx("host_responded")]).strip().lower() == "yes"
        rating_raw = float(row[idx("rating_raw")])
        rating_scale = int(row[idx("rating_scale")])

        review: Dict[str, Any] = {
            "id":             review_id,
            "platform":       str(row[idx("platform")]).strip(),
            "property_id":    str(row[idx("property_id")]).strip(),
            "property_name":  str(row[idx("property_name")]).strip(),
            "location":       str(row[idx("location")]).strip(),
            "caretaker_id":   str(row[idx("caretaker_id")]).strip(),
            "caretaker_name": str(row[idx("caretaker_name")]).strip(),
            "rating_raw":     rating_raw,
            "rating_scale":   rating_scale,
            "host_responded": host_resp,
            "guest_name":     str(row[idx("guest_name")]).strip(),
            "review_text":    str(row[idx("review_text")]).strip(),
        }

        # Apply special business-rule flags
        if review_id in NOISE_FLAGS:
            review["noise_flag"] = NOISE_FLAGS[review_id]

        if review_id in RESOLVED_FLAGS_EXCEL:
            review["resolved_flag"] = RESOLVED_FLAGS_EXCEL[review_id]

        reviews.append(review)

    wb.close()
    print(f"[reviews] Loaded {len(reviews)} reviews from Excel: {EXCEL_PATH.name}")
    return reviews


# Load once at module import time — used by main.py
REVIEWS: List[Dict[str, Any]] = _load_reviews_from_excel()
