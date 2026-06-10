import json
import os
import re
import time
import google.generativeai as genai
from typing import List, Dict, Any
from utils.normalize import normalize_rating

# Reads GEMINI_API_KEY from environment (set via .env + dotenv)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Free tier: gemini-2.5-flash (5 RPM / 20 RPD on free tier)
MODEL_NAME = "gemini-2.5-flash"

# Retry settings for 429 rate-limit errors
# Free tier = 5 RPM → 1 request per 12s minimum, so wait 15s to be safe
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 15

SYSTEM_PROMPT = (
    "You are a senior hospitality operations analyst for Spacez, "
    "a premium villa rental company in India. "
    "Analyze guest reviews and extract structured, actionable insights. "
    "CRITICAL: Return ONLY raw valid JSON. "
    "No markdown. No backticks. No ```json. No explanation. No preamble. No trailing text. "
    "Start your response with { and end with }. "
    "Keep ALL string values SHORT (under 80 characters) to avoid truncation. "
    "Never invent issues not explicitly mentioned in the reviews."
)


def build_user_prompt(property_name: str, reviews: List[Dict[str, Any]]) -> str:
    lines = []
    for i, r in enumerate(reviews, 1):
        norm = normalize_rating(r["rating_raw"], r["rating_scale"])
        resolved = f" [RESOLVED CONFIRMED: {r['resolved_flag']}]" if r.get("resolved_flag") else ""
        # Truncate review text to avoid hitting token limits
        text = r["review_text"][:300]
        lines.append(f'{i}. [{r["platform"]} · {norm}/10]{resolved} "{text}"')

    return f"""Analyze these {len(reviews)} guest reviews for {property_name}.

{chr(10).join(lines)}

RULES:
- CRITICAL = failure in 2+ reviews OR single severe incident
- RECURRING = same issue in 2+ reviews
- ONE_OFF = single mention
- caretaker_controllable=false: wifi, road, listing photos, occupancy policy, mosquitoes, humidity, blocked views, construction
- caretaker_controllable=true: check-in timing, cleanliness, responsiveness, extra arrangements, maintenance

Return ONLY this JSON (no markdown, no backticks, start with {{):
{{
  "avg_normalized_rating": <number 0-10>,
  "recurring_issues": [
    {{
      "issue": "<max 40 chars>",
      "severity": "CRITICAL|RECURRING|ONE_OFF",
      "review_count": <integer>,
      "caretaker_controllable": <boolean>,
      "recommended_action": "<max 60 chars>",
      "supporting_evidence": "<max 60 chars>"
    }}
  ],
  "what_works_well": ["<max 50 chars>", "<max 50 chars>"],
  "noise_excluded_reasons": ["<reason if any excluded>"],
  "resolved_issues": ["<issue if resolved>"]
}}"""


def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from Gemini response.
    Handles: markdown fences, leading text, truncated output.
    """
    # 1. Strip markdown code fences
    text = text.replace("```json", "").replace("```", "").strip()

    # 2. Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Find first { ... } block via regex
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 4. Truncated JSON recovery — find last complete field before cut-off
    # Try trimming from the last complete key-value before truncation
    brace_open = text.find('{')
    if brace_open != -1:
        fragment = text[brace_open:]
        # Close any open arrays/objects by counting braces
        depth = 0
        last_valid = brace_open
        for i, ch in enumerate(fragment):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    last_valid = i + 1
                    break
        # Try extracting up to last complete closing brace
        candidate = fragment[:last_valid]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("Could not extract valid JSON", text, 0)


def analyze_property(property_name: str, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Call Gemini API for one property with retry on 429. Returns parsed dict or fallback."""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=SYSTEM_PROMPT,
            )
            response = model.generate_content(
                build_user_prompt(property_name, reviews),
                generation_config=genai.GenerationConfig(
                    temperature=0.1,           # very low = most deterministic JSON
                    max_output_tokens=2048,    # ↑ increased from 1200 to prevent truncation
                ),
            )
            raw = response.text
            print(f"[Gemini] Raw response for {property_name} ({len(raw)} chars): {raw[:120]}…")
            result = _extract_json(raw)
            print(f"[Gemini] ✓ Parsed OK for {property_name}")
            return result

        except json.JSONDecodeError as e:
            print(f"[Gemini] JSON parse error for {property_name}: {e}")
            if attempt < MAX_RETRIES:
                print(f"[Gemini] Retrying {property_name} in {RETRY_DELAY_SECONDS}s…")
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            return {
                "avg_normalized_rating": None,
                "recurring_issues": [],
                "what_works_well": [],
                "noise_excluded_reasons": ["AI response could not be parsed"],
                "resolved_issues": [],
                "api_error": True,
            }

        except Exception as e:
            err_str = str(e)
            # Retry on 429 rate-limit errors
            if "429" in err_str and attempt < MAX_RETRIES:
                print(f"[Gemini] Rate limited for {property_name} (attempt {attempt}/{MAX_RETRIES}). "
                      f"Retrying in {RETRY_DELAY_SECONDS}s…")
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            print(f"[Gemini] API error for {property_name}: {e}")
            return {
                "avg_normalized_rating": None,
                "recurring_issues": [],
                "what_works_well": [],
                "noise_excluded_reasons": ["AI service unavailable"],
                "resolved_issues": [],
                "api_error": True,
            }
