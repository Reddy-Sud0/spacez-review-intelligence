from typing import List, Dict, Any

NON_CARETAKER_FAULT_KEYWORDS = [
    "wifi", "internet", "road", "photo", "listing", "mislead",
    "occupancy", "policy", "parking", "mosquito", "damp",
    "location", "restaurant", "nearby", "humid", "view",
    "building", "blocked", "construction", "oversold", "bedroom"
]

NOISE_REVIEW_IDS = {
    "RV035": "Occupancy policy complaint — listing issue, not hospitality failure",
    "RV041": "Too vague ('Amazing.') — no actionable signal"
}

CROSS_PROPERTY_CARETAKERS = {
    "CT03": {
        "name": "Lokesh Gowda",
        "properties": ["P03", "P04"],
        "pattern": "Check-in delays appear across both Misty Estate and Coorg Canopy. This follows the caretaker, not either property."
    }
}

RESOLVED_FLAGS = {
    "RV036": {
        "property_id": "P01",
        "issue": "Pool cleanliness",
        "note": "Repeat guest (RV036) confirms pool was clean — issue appears resolved."
    }
}

RESOLVED_PROPERTY_IDS = ["P01"]


def is_caretaker_controllable(review_text: str) -> bool:
    """Return False if review mentions infrastructure/listing issues outside caretaker control."""
    text = review_text.lower()
    return not any(kw in text for kw in NON_CARETAKER_FAULT_KEYWORDS)


def filter_noise(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Exclude noise reviews from AI analysis (policy complaints, too-vague reviews)."""
    return [r for r in reviews if r["id"] not in NOISE_REVIEW_IDS]


def get_property_fault_issues(reviews: List[Dict[str, Any]]) -> List[str]:
    """Return list of property-level issues (not caretaker's fault) for a set of reviews."""
    issues = []
    combined = " ".join(r["review_text"].lower() for r in reviews)
    if any(k in combined for k in ["wifi", "internet"]):
        issues.append("WiFi infrastructure (ops/tech team)")
    if "road" in combined:
        issues.append("Road access condition (listing team)")
    if any(k in combined for k in ["photo", "mislead"]):
        issues.append("Listing photo accuracy (listing team)")
    if any(k in combined for k in ["pool", "green", "murky"]):
        issues.append("Pool maintenance contractor (ops team)")
    if any(k in combined for k in ["heat", "heater", "cold"]):
        issues.append("Heating system (ops maintenance)")
    if any(k in combined for k in ["mosquito"]):
        issues.append("Mosquito/pest control (environmental — not caretaker)")
    if any(k in combined for k in ["damp", "humid"]):
        issues.append("Humidity/dampness (property characteristic — not caretaker)")
    return list(set(issues))
