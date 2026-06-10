import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List

# ⚠️ MUST load .env BEFORE importing gemini_service,
# because gemini_service calls genai.configure() at import time.
load_dotenv(override=True)

from data.reviews import REVIEWS
from utils.normalize import avg_normalized_rating, response_rate, rating_tier, normalize_rating
from utils.grouping import group_by_property, group_by_caretaker
from utils.rules import (
    filter_noise, is_caretaker_controllable, get_property_fault_issues,
    CROSS_PROPERTY_CARETAKERS, NOISE_REVIEW_IDS,
    RESOLVED_FLAGS, RESOLVED_PROPERTY_IDS
)
from services.gemini_service import analyze_property
from models.schemas import AnalysisResponse, PropertyAnalysis, CaretakerDigest, BusinessMetrics, IssueItem

app = FastAPI(
    title="Spacez Review Intelligence API",
    description="AI-powered review analysis for Spacez premium villa properties",
    version="1.0.0"
)

# CORS — allow Vercel, Netlify, and local dev automatically
# FRONTEND_URL in .env / Render env vars can be your exact production URL
_frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = list(filter(None, [
    _frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.(vercel\.app|netlify\.app)$",  # all Vercel/Netlify previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check — confirms API is up, reviews are loaded, and AI key is set."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return {
        "status": "ok",
        "reviews_loaded": len(REVIEWS),
        "ai_key_configured": bool(api_key),
        "ai_model": "gemini-2.5-flash",
    }


@app.get("/api/status")
def get_status():
    """
    AI readiness check — validates key is configured without burning RPD quota.
    Free tier: gemini-2.5-flash = 5 RPM / 20 RPD. We save all calls for analysis.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return {
            "ai_available": False,
            "model": None,
            "reason": "GEMINI_API_KEY not set in .env",
        }
    # Key is present and looks valid (starts with AIza = Google API key format)
    key_looks_valid = api_key.startswith("AIza") and len(api_key) > 30
    return {
        "ai_available": key_looks_valid,
        "model": "gemini-2.5-flash",
        "reason": "API key configured" if key_looks_valid else "Key format looks invalid (should start with AIza)",
        "quota_note": "Free tier: 5 RPM / 20 RPD — quota reserved for analysis calls",
    }


@app.get("/api/reviews")
def get_reviews():
    """Return all raw reviews — useful for debugging and verifying data integrity."""
    return {"reviews": REVIEWS, "count": len(REVIEWS)}


@app.get("/api/analyze", response_model=AnalysisResponse)
def run_full_analysis():
    """
    Main endpoint. Runs Gemini AI analysis on all 7 properties sequentially.
    Returns complete structured data for all 3 stakeholder tabs:
      - ops:        Per-property priority action board (sorted worst first)
      - business:   Portfolio scorecard + strategic signals
      - caretaker:  Hospitality-only coaching digests (non-controllable issues filtered)

    Called once when user clicks 'Run Analysis'. Takes ~20-40s (7 Gemini API calls).
    """
    properties = group_by_property(REVIEWS)
    caretakers = group_by_caretaker(REVIEWS)

    # ── OPS TAB ──────────────────────────────────────────────────────────────
    ops_results: List[PropertyAnalysis] = []

    for prop in properties:
        # Filter noise reviews BEFORE sending to Gemini
        clean_reviews = filter_noise(prop["reviews"])
        ai = analyze_property(prop["property_name"], clean_reviews)

        # Use Gemini's avg if available, fallback to local math
        avg = ai.get("avg_normalized_rating") or avg_normalized_rating(clean_reviews)
        platforms = list(set(r["platform"] for r in prop["reviews"]))

        # Cross-property caretaker check (Lokesh Gowda / CT03)
        cross = CROSS_PROPERTY_CARETAKERS.get(prop["caretaker_id"])

        # Resolved issue check (Serenity Villa pool)
        has_resolved = prop["property_id"] in RESOLVED_PROPERTY_IDS
        resolved_note = None
        if has_resolved:
            for flag in RESOLVED_FLAGS.values():
                if flag["property_id"] == prop["property_id"]:
                    resolved_note = flag["note"]
                    break

        # Build typed IssueItem list from Gemini's JSON
        issues = []
        for item in ai.get("recurring_issues", []):
            issues.append(IssueItem(
                issue=item.get("issue", ""),
                severity=item.get("severity", "ONE_OFF"),
                review_count=item.get("review_count", 1),
                caretaker_controllable=item.get("caretaker_controllable", True),
                recommended_action=item.get("recommended_action", ""),
                supporting_evidence=item.get("supporting_evidence", "")
            ))

        # Sort: CRITICAL first → RECURRING → ONE_OFF
        severity_order = {"CRITICAL": 0, "RECURRING": 1, "ONE_OFF": 2}
        issues.sort(key=lambda x: severity_order.get(x.severity, 3))

        ops_results.append(PropertyAnalysis(
            property_id=prop["property_id"],
            property_name=prop["property_name"],
            location=prop["location"],
            caretaker_id=prop["caretaker_id"],
            caretaker_name=prop["caretaker_name"],
            review_count=len(prop["reviews"]),
            platforms=platforms,
            avg_normalized_rating=avg,
            rating_tier=rating_tier(avg),
            response_rate=response_rate(prop["reviews"]),
            is_cross_property_caretaker=bool(cross),
            cross_property_pattern=cross["pattern"] if cross else None,
            has_resolved_issue=has_resolved,
            resolved_issue_note=resolved_note,
            recurring_issues=issues,
            what_works_well=ai.get("what_works_well", []),
            noise_excluded_reasons=ai.get("noise_excluded_reasons", []),
            api_error=ai.get("api_error", False)
        ))

    # Sort ops cards: worst rated first (most urgent at top)
    ops_results.sort(key=lambda x: x.avg_normalized_rating)

    # ── BUSINESS TAB ─────────────────────────────────────────────────────────
    portfolio_avg = avg_normalized_rating(REVIEWS)
    port_response_rate = response_rate(REVIEWS)
    critical_count = sum(
        1 for p in ops_results
        for issue in p.recurring_issues
        if issue.severity == "CRITICAL"
    )

    # Portfolio table: best rated first (business wants to see stars at top)
    portfolio_rows = []
    for p in sorted(ops_results, key=lambda x: -x.avg_normalized_rating):
        portfolio_rows.append({
            "property_id": p.property_id,
            "property_name": p.property_name,
            "location": p.location,
            "caretaker_name": p.caretaker_name,
            "avg_rating": p.avg_normalized_rating,
            "rating_tier": p.rating_tier,
            "response_rate": p.response_rate,
            "review_count": p.review_count,
            "has_resolved": p.has_resolved_issue,
            "critical_count": sum(1 for i in p.recurring_issues if i.severity == "CRITICAL"),
            "platforms": p.platforms,
        })

    # Strategic signals — hardcoded as spec dictates
    signals = [
        {"type": "STAR",     "property": "Backwater Bungalow", "message": "Portfolio best performer. Biju Thomas sets the hospitality benchmark. Replicate his caretaker model across other properties."},
        {"type": "ACTION",   "property": "Hilltop Haven",      "message": "Listing accuracy is a business risk. Misleading photos + broken WiFi are driving 2-star reviews. Review investment or update listing immediately."},
        {"type": "WATCH",    "property": "Vineyard Villa",      "message": "Housekeeping vendor reliability is critical. Cleanliness failures across 4+ reviews signal SLA breakdown. Contract review required."},
        {"type": "RESOLVED", "property": "Serenity Villa",      "message": "RV036 (repeat guest Aarti Menon) confirms pool was clean. Monitor to confirm sustained improvement over next 60 days."},
        {"type": "NOTE",     "property": "Hilltop Haven",       "message": "RV035 occupancy policy complaint excluded from hospitality scoring — this is a listing clarity issue, not a caretaker failure."},
    ]

    business = BusinessMetrics(
        portfolio_avg=portfolio_avg,
        response_rate=port_response_rate,
        total_properties=len(ops_results),
        critical_issues_count=critical_count,
        portfolio_rows=portfolio_rows,
        signals=signals
    )

    # ── CARETAKER TAB ─────────────────────────────────────────────────────────
    caretaker_digests: List[CaretakerDigest] = []

    for ct in caretakers:
        # FAIRNESS: only score on caretaker-controllable reviews
        controllable = [r for r in ct["reviews"] if is_caretaker_controllable(r["review_text"])]
        ct_score = avg_normalized_rating(controllable) if controllable else 0.0

        cross = CROSS_PROPERTY_CARETAKERS.get(ct["caretaker_id"])

        # Detect most impactful single improvement area
        checkin_issues = [
            r for r in ct["reviews"]
            if any(k in r["review_text"].lower() for k in ["check-in", "late", "arrived late", "unreachable", "delay", "nobody was there", "setup took"])
        ]
        clean_issues = [
            r for r in ct["reviews"]
            if any(k in r["review_text"].lower() for k in ["clean", "dirty", "dishes", "bedsheet", "housekeep", "hair in"])
        ]

        one_thing = None
        if len(checkin_issues) >= 2:
            one_thing = f"Check-in punctuality — late arrivals mentioned in {len(checkin_issues)} reviews"
        elif len(clean_issues) >= 2:
            one_thing = f"Pre-arrival cleanliness coordination with housekeeping vendor ({len(clean_issues)} reviews)"

        # Pull positive quotes from high-rated controllable reviews (max 3)
        loved = []
        for r in controllable:
            norm = normalize_rating(r["rating_raw"], r["rating_scale"])
            if norm >= 8.0:
                snippet = r["review_text"][:80] + ("…" if len(r["review_text"]) > 80 else "")
                loved.append(snippet)
        loved = loved[:3]

        # Property-level faults (shown in separate section, not used in score)
        property_faults = get_property_fault_issues(ct["reviews"])

        caretaker_digests.append(CaretakerDigest(
            caretaker_id=ct["caretaker_id"],
            caretaker_name=ct["caretaker_name"],
            properties=ct["properties"],
            total_reviews=len(ct["reviews"]),
            hospitality_score=ct_score,
            rating_tier=rating_tier(ct_score),
            is_multi_property=len(ct["properties"]) > 1,
            cross_property_warning=cross["pattern"] if cross else None,
            what_guests_loved=loved,
            one_thing_to_improve=one_thing,
            property_fault_issues=property_faults
        ))

    # Sort caretakers: best score first
    caretaker_digests.sort(key=lambda x: -x.hospitality_score)

    return AnalysisResponse(ops=ops_results, business=business, caretaker=caretaker_digests)
