from typing import List, Dict, Any
from collections import defaultdict


def group_by_property(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group reviews by property_id. Returns list of property dicts with embedded reviews."""
    groups: Dict[str, Dict] = {}
    for r in reviews:
        pid = r["property_id"]
        if pid not in groups:
            groups[pid] = {
                "property_id": pid,
                "property_name": r["property_name"],
                "location": r["location"],
                "caretaker_id": r["caretaker_id"],
                "caretaker_name": r["caretaker_name"],
                "reviews": []
            }
        groups[pid]["reviews"].append(r)
    return list(groups.values())


def group_by_caretaker(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group reviews by caretaker_id. Returns list of caretaker dicts with embedded reviews."""
    groups: Dict[str, Dict] = {}
    for r in reviews:
        cid = r["caretaker_id"]
        if cid not in groups:
            groups[cid] = {
                "caretaker_id": cid,
                "caretaker_name": r["caretaker_name"],
                "properties": [],
                "reviews": []
            }
        ct = groups[cid]
        if r["property_name"] not in ct["properties"]:
            ct["properties"].append(r["property_name"])
        ct["reviews"].append(r)
    return list(groups.values())
