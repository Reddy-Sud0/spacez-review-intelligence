import json
import anthropic
from typing import List, Dict, Any
from utils.normalize import normalize_rating

# Reads ANTHROPIC_API_KEY from environment automatically (set via .env + dotenv)
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a senior hospitality operations analyst for Spacez, a premium villa rental company in India.
Analyze guest reviews and extract structured, actionable insights.
Return ONLY valid JSON. No markdown. No backticks. No explanation. No preamble.
Never invent issues not explicitly mentioned in the reviews."""


def build_user_prompt(property_name: str, reviews: List[Dict[str, Any]]) -> str:
    lines = []
    for i, r in enumerate(reviews, 1):
        norm = normalize_rating(r["rating_raw"], r["rating_scale"])
        resolved = f" [RESOLVED CONFIRMED: {r['resolved_flag']}]" if r.get("resolved_flag") else ""
        lines.append(f"{i}. [{r['platform']} · {norm}/10]{resolved} \"{r['review_text']}\"")

    return f"""Analyze these {len(reviews)} guest reviews for {property_name}.

{chr(10).join(lines)}

CLASSIFICATION RULES:
- CRITICAL = comfort/safety failure in 2+ reviews OR single severe incident
- RECURRING = same issue mentioned in 2+ reviews
- ONE_OFF = single mention worth flagging
- caretaker_controllable = false for: wifi infrastructure, road condition, listing photos, occupancy policy, mosquitoes, humidity, blocked views, construction
- caretaker_controllable = true for: check-in timing, cleanliness coordination, responsiveness, extra arrangements, maintenance escalation

Return exactly this JSON:
{{
  "avg_normalized_rating": <number 0-10>,
  "recurring_issues": [
    {{
      "issue": "<short label>",
      "severity": "CRITICAL|RECURRING|ONE_OFF",
      "review_count": <integer>,
      "caretaker_controllable": <boolean>,
      "recommended_action": "<specific action for ops team>",
      "supporting_evidence": "<one sentence paraphrase, max 20 words>"
    }}
  ],
  "what_works_well": ["<item1>", "<item2>"],
  "noise_excluded_reasons": ["<reason if any review excluded>"],
  "resolved_issues": ["<issue label if resolved_flag review confirms fix>"]
}}"""


def analyze_property(property_name: str, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Call Claude API for one property. Returns parsed dict or fallback on error."""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": build_user_prompt(property_name, reviews)
            }]
        )
        raw = message.content[0].text
        # Strip any accidental markdown code fences
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[Claude] JSON parse error for {property_name}: {e}")
        return {
            "avg_normalized_rating": None,
            "recurring_issues": [],
            "what_works_well": [],
            "noise_excluded_reasons": ["AI response could not be parsed"],
            "resolved_issues": [],
            "api_error": True
        }
    except Exception as e:
        print(f"[Claude] API error for {property_name}: {e}")
        return {
            "avg_normalized_rating": None,
            "recurring_issues": [],
            "what_works_well": [],
            "noise_excluded_reasons": ["AI service unavailable"],
            "resolved_issues": [],
            "api_error": True
        }
