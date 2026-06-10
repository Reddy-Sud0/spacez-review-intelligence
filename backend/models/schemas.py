from pydantic import BaseModel
from typing import List, Optional


class IssueItem(BaseModel):
    issue: str
    severity: str               # "CRITICAL" | "RECURRING" | "ONE_OFF"
    review_count: int
    caretaker_controllable: bool
    recommended_action: str
    supporting_evidence: str


class PropertyAnalysis(BaseModel):
    property_id: str
    property_name: str
    location: str
    caretaker_id: str
    caretaker_name: str
    review_count: int
    platforms: List[str]
    avg_normalized_rating: float
    rating_tier: str            # "good" | "mid" | "bad"
    response_rate: int
    is_cross_property_caretaker: bool
    cross_property_pattern: Optional[str] = None
    has_resolved_issue: bool
    resolved_issue_note: Optional[str] = None
    recurring_issues: List[IssueItem]
    what_works_well: List[str]
    noise_excluded_reasons: List[str]
    api_error: bool


class CaretakerDigest(BaseModel):
    caretaker_id: str
    caretaker_name: str
    properties: List[str]
    total_reviews: int
    hospitality_score: float    # avg of ONLY controllable reviews
    rating_tier: str
    is_multi_property: bool
    cross_property_warning: Optional[str] = None
    what_guests_loved: List[str]
    one_thing_to_improve: Optional[str] = None
    property_fault_issues: List[str]


class BusinessMetrics(BaseModel):
    portfolio_avg: float
    response_rate: int
    total_properties: int
    critical_issues_count: int
    portfolio_rows: List[dict]
    signals: List[dict]


class AnalysisResponse(BaseModel):
    ops: List[PropertyAnalysis]
    business: BusinessMetrics
    caretaker: List[CaretakerDigest]
