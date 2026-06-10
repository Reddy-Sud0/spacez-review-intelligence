from typing import List, Dict, Any


def normalize_rating(raw: float, scale: int) -> float:
    """Normalize any rating to /10. Airbnb /5 → ×2, Booking /10 → as-is, Google /5 → ×2."""
    return round((raw / scale) * 10, 1)


def avg_normalized_rating(reviews: List[Dict[str, Any]]) -> float:
    """Compute average normalized rating across a list of reviews."""
    if not reviews:
        return 0.0
    total = sum(normalize_rating(r["rating_raw"], r["rating_scale"]) for r in reviews)
    return round(total / len(reviews), 1)


def response_rate(reviews: List[Dict[str, Any]]) -> int:
    """Return percentage of reviews where host responded (0-100)."""
    if not reviews:
        return 0
    responded = sum(1 for r in reviews if r.get("host_responded"))
    return round((responded / len(reviews)) * 100)


def rating_tier(score: float) -> str:
    """Classify a score into good/mid/bad tier."""
    if score >= 7.5:
        return "good"
    elif score >= 5.5:
        return "mid"
    return "bad"
