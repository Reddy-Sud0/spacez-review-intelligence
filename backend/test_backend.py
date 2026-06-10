import sys
sys.path.insert(0, '.')

from data.reviews import REVIEWS
from utils.normalize import avg_normalized_rating, normalize_rating, rating_tier
from utils.grouping import group_by_property, group_by_caretaker
from utils.rules import filter_noise, CROSS_PROPERTY_CARETAKERS, NOISE_REVIEW_IDS

print("=== Rating Normalization ===")
print("Airbnb 4/5   ->", normalize_rating(4.0, 5))    # expect 8.0
print("Booking 6/10 ->", normalize_rating(6.0, 10))   # expect 6.0
print("Google 3/5   ->", normalize_rating(3.0, 5))    # expect 6.0

print(f"\n=== Noise Filter: {len(REVIEWS)} -> ", end="")
clean = filter_noise(REVIEWS)
print(f"{len(clean)} reviews ===")
excluded = [r["id"] for r in REVIEWS if r["id"] in NOISE_REVIEW_IDS]
print("Excluded:", excluded)

print("\n=== Properties (sorted worst first) ===")
props = group_by_property(clean)
props_sorted = sorted(props, key=lambda p: avg_normalized_rating(p["reviews"]))
for p in props_sorted:
    avg = avg_normalized_rating(p["reviews"])
    tier = rating_tier(avg)
    print(f"  {p['property_name']:25} | {len(p['reviews']):2} reviews | {avg}/10 [{tier}]")

print("\n=== Cross-Property Caretaker Alert ===")
ct03 = CROSS_PROPERTY_CARETAKERS.get("CT03")
print(f"CT03 name: {ct03['name']}")
print(f"CT03 properties: {ct03['properties']}")
print(f"CT03 pattern: {ct03['pattern']}")

print("\n=== Caretakers ===")
cts = group_by_caretaker(REVIEWS)
for ct in cts:
    print(f"  {ct['caretaker_name']:15} | {len(ct['properties'])} prop(s) | {len(ct['reviews'])} reviews")

print("\n=== All checks PASSED ===")
