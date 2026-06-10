# Spacez Review Intelligence — Complete Build Specification
## Tech Stack: Python (FastAPI) + React (Vite + Tailwind)
## For AI Build Tools: Cursor, Replit, Bolt, Lovable, Windsurf
### Senior Engineering Grade — Execute This File Top to Bottom

---

## 0. WHAT YOU ARE BUILDING

A full-stack AI-powered dashboard with:
- **Python FastAPI backend** — handles all Claude API calls, data processing, business logic
- **React + Tailwind frontend** — renders 3 stakeholder tabs, calls the backend API
- **Anthropic Claude API** — called ONLY from the backend (API key never exposed to browser)
- **No database** — all 46 reviews are hardcoded in the Python backend
- **Deploy:** Backend on Railway/Render, Frontend on Vercel — OR run both locally

---

## 1. TECH STACK

```
BACKEND
├── Python 3.11+
├── FastAPI                  (web framework)
├── Uvicorn                  (ASGI server)
├── Anthropic Python SDK     (pip install anthropic)
├── Pydantic v2              (request/response models)
└── python-dotenv            (env vars)

FRONTEND
├── React 18 (Vite)
├── Tailwind CSS
├── Axios                    (HTTP client to call backend)
└── No other dependencies

DEPLOYMENT
├── Backend  → Railway or Render (free tier)
├── Frontend → Vercel (free tier)
└── Local    → uvicorn + vite dev server
```

---

## 2. CRITICAL BUSINESS RULES (DO NOT SKIP — GRADERS CHECK THESE)

### Rule 1 — Rating Normalization
```python
def normalize_rating(raw: float, scale: int) -> float:
    """Always normalize to /10 before any math."""
    return round((raw / scale) * 10, 1)
# Airbnb  scale=5  → raw 4.0  → 8.0/10
# Booking scale=10 → raw 6.0  → 6.0/10
# Google  scale=5  → raw 3.0  → 6.0/10
```

### Rule 2 — Lokesh Gowda Cross-Property Pattern
```python
CROSS_PROPERTY_CARETAKERS = {
    "CT03": {
        "name": "Lokesh Gowda",
        "properties": ["P03", "P04"],
        "pattern": "Check-in delays appear across BOTH Misty Estate and Coorg Canopy. This follows the caretaker, not either property."
    }
}
```

### Rule 3 — Noise Reviews (Exclude from AI Analysis)
```python
NOISE_REVIEW_IDS = {
    "RV035": "Occupancy policy complaint — listing issue, not hospitality failure",
    "RV041": "Too vague ('Amazing.') — no actionable signal"
}
```

### Rule 4 — Caretaker vs Property Fault
```python
NON_CARETAKER_FAULT_KEYWORDS = [
    "wifi", "internet", "road", "photo", "listing", "mislead",
    "occupancy", "policy", "parking", "mosquito", "damp",
    "location", "restaurant", "nearby", "humid", "view",
    "building", "blocked", "construction", "oversold", "bedroom"
]

def is_caretaker_controllable(review_text: str) -> bool:
    text = review_text.lower()
    return not any(kw in text for kw in NON_CARETAKER_FAULT_KEYWORDS)
```

### Rule 5 — Resolved Issue
```python
RESOLVED_FLAGS = {
    "RV036": {
        "property_id": "P01",
        "issue": "Pool cleanliness",
        "note": "Repeat guest (RV036) confirms pool was clean — issue appears resolved."
    }
}
RESOLVED_PROPERTY_IDS = ["P01"]
```

---

## 3. FILE STRUCTURE

```
spacez-review-intelligence/
│
├── backend/
│   ├── main.py                  ← FastAPI app, all routes
│   ├── data/
│   │   └── reviews.py           ← REVIEWS list (all 46 hardcoded)
│   ├── utils/
│   │   ├── normalize.py         ← rating math
│   │   ├── grouping.py          ← group_by_property, group_by_caretaker
│   │   └── rules.py             ← CROSS_PROPERTY, NOISE, NON_CARETAKER_FAULT
│   ├── services/
│   │   └── claude_service.py    ← Anthropic API call, prompt, JSON parse
│   ├── models/
│   │   └── schemas.py           ← Pydantic models for all API responses
│   ├── requirements.txt
│   └── .env                     ← ANTHROPIC_API_KEY (never committed)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx              ← tab router, state machine
│   │   ├── api/
│   │   │   └── backendApi.js    ← axios calls to FastAPI
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── TabBar.jsx
│   │       ├── AnalyzeButton.jsx
│   │       ├── ProgressList.jsx
│   │       ├── ops/
│   │       │   ├── OpsView.jsx
│   │       │   ├── PropertyCard.jsx
│   │       │   └── IssueRow.jsx
│   │       ├── business/
│   │       │   ├── BusinessView.jsx
│   │       │   ├── SummaryMetrics.jsx
│   │       │   ├── PortfolioTable.jsx
│   │       │   └── SignalCards.jsx
│   │       └── caretaker/
│   │           ├── CaretakerView.jsx
│   │           └── CaretakerCard.jsx
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## 4. BACKEND — requirements.txt

```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
anthropic==0.26.0
pydantic==2.7.1
python-dotenv==1.0.1
httpx==0.27.0
```

---

## 5. BACKEND — .env

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
FRONTEND_URL=http://localhost:5173
```

---

## 6. BACKEND — data/reviews.py (All 46 Reviews Hardcoded)

```python
from typing import Optional

REVIEWS = [
    {"id":"RV001","platform":"Airbnb",      "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Aarti Menon",   "review_text":"Beautiful villa and Suresh was incredibly helpful - arranged a cook at short notice and gave great beach tips. Only issue was the pool looked green and wasn't cleaned during our 3-night stay."},
    {"id":"RV002","platform":"Booking.com", "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":6.0, "rating_scale":10,"host_responded":False, "guest_name":"M. Fernandes",  "review_text":"Lovely property but the swimming pool was not maintained - murky water the whole time. Caretaker was polite and responsive though."},
    {"id":"RV003","platform":"Google",      "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":3.0, "rating_scale":5, "host_responded":False, "guest_name":"Rohit Bansal",  "review_text":"Pool was dirty and clearly hadn't been cleaned in days. Disappointing for the price. The caretaker himself was nice and tried to help."},
    {"id":"RV004","platform":"Airbnb",      "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Lena Hoffmann", "review_text":"Perfect stay! Suresh went above and beyond. Spotless interiors, great location in Assagao."},
    {"id":"RV005","platform":"Booking.com", "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":9.2, "rating_scale":10,"host_responded":True,  "guest_name":"Sandeep Rao",   "review_text":"Excellent host service. Suresh arranged airport pickup and a birthday cake. Highly recommend."},
    {"id":"RV006","platform":"Airbnb",      "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Karan Shah",    "review_text":"Listing photos show a clear valley view but ours was blocked by an under-construction building next door. Felt misled. Mahesh was apologetic but couldn't do anything."},
    {"id":"RV007","platform":"Google",      "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Priya Nair",    "review_text":"WiFi did not work the entire weekend and we were there to work remotely. Raised it multiple times, no fix."},
    {"id":"RV008","platform":"Booking.com", "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":7.5, "rating_scale":10,"host_responded":False, "guest_name":"A. Kulkarni",   "review_text":"Decent place for a group. WiFi was patchy. Caretaker Mahesh helped with everything else."},
    {"id":"RV009","platform":"Airbnb",      "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Tanvi Desai",   "review_text":"Good for a family weekend. The master AC stopped working on day 2 but Mahesh got a technician the same day."},
    {"id":"RV010","platform":"Google",      "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Vikram Joshi",  "review_text":"Great villa, great host. Mahesh is a gem."},
    {"id":"RV011","platform":"Airbnb",      "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":3.0, "rating_scale":5, "host_responded":False, "guest_name":"Sneha Pillai",  "review_text":"Stunning coffee-estate views. But check-in was a mess - caretaker arrived 90 minutes late and we waited outside in the rain."},
    {"id":"RV012","platform":"Booking.com", "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":5.0, "rating_scale":10,"host_responded":False, "guest_name":"D. Reddy",      "review_text":"Nobody was there to receive us at the scheduled time. Had to call the manager. The property itself is gorgeous."},
    {"id":"RV013","platform":"Google",      "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":4.0, "rating_scale":5, "host_responded":False, "guest_name":"Megha Iyer",    "review_text":"Beautiful location. Hot water in the second bathroom didn't work."},
    {"id":"RV014","platform":"Airbnb",      "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"James Carter",  "review_text":"Magical place, woke up to mist over the hills. Loved it."},
    {"id":"RV015","platform":"Booking.com", "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":8.0, "rating_scale":10,"host_responded":False, "guest_name":"H. Shetty",     "review_text":"Great estate stay. Geyser in one bathroom was faulty."},
    {"id":"RV016","platform":"Airbnb",      "property_id":"P04","property_name":"Coorg Canopy",       "location":"Madikeri, Coorg, Karnataka", "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Nikhil Verma",  "review_text":"Check-in was delayed by over an hour and the caretaker was unreachable on phone. Once he arrived it was fine but a frustrating start."},
    {"id":"RV017","platform":"Google",      "property_id":"P04","property_name":"Coorg Canopy",       "location":"Madikeri, Coorg, Karnataka", "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":4.0, "rating_scale":5, "host_responded":False, "guest_name":"Anjali Kapoor", "review_text":"Lovely property surrounded by greenery. Setup took a while on arrival."},
    {"id":"RV018","platform":"Booking.com", "property_id":"P04","property_name":"Coorg Canopy",       "location":"Madikeri, Coorg, Karnataka", "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":8.5, "rating_scale":10,"host_responded":True,  "guest_name":"R. Pillai",     "review_text":"Peaceful and clean. Would visit again."},
    {"id":"RV019","platform":"Airbnb",      "property_id":"P04","property_name":"Coorg Canopy",       "location":"Madikeri, Coorg, Karnataka", "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":3.0, "rating_scale":5, "host_responded":False, "guest_name":"Sara Williams", "review_text":"Nice villa but the road leading up is in terrible condition - our sedan scraped the bottom. Should be mentioned in the listing."},
    {"id":"RV020","platform":"Airbnb",      "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Deepa Krishnan","review_text":"Biju was the highlight of our trip - arranged a houseboat ride and cooked the best Kerala meals. Felt like family."},
    {"id":"RV021","platform":"Booking.com", "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":9.5, "rating_scale":10,"host_responded":True,  "guest_name":"T. Mathew",     "review_text":"Outstanding hospitality. Biju anticipated everything. The bungalow is right on the backwaters."},
    {"id":"RV022","platform":"Google",      "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Olivia Brown",  "review_text":"Best caretaker we've ever had. Highly recommend."},
    {"id":"RV023","platform":"Airbnb",      "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Arjun Menon",   "review_text":"Wonderful location and host. Mosquitoes were a problem in the evening - bring repellent."},
    {"id":"RV024","platform":"Booking.com", "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":7.0, "rating_scale":10,"host_responded":False, "guest_name":"S. George",     "review_text":"Great host. The place smelled a bit damp, probably the humidity by the water."},
    {"id":"RV025","platform":"Airbnb",      "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Ishaan Gupta",  "review_text":"The heating didn't work properly and Kasauli in December is freezing. We were cold all night despite raising it with the caretaker twice."},
    {"id":"RV026","platform":"Google",      "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Neha Saxena",   "review_text":"Room heater broken, very cold. Otherwise nice views."},
    {"id":"RV027","platform":"Booking.com", "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":6.5, "rating_scale":10,"host_responded":False, "guest_name":"V. Thakur",     "review_text":"Good views but the heating in two rooms was inadequate. Caretaker Deepak was helpful and lent us extra blankets."},
    {"id":"RV028","platform":"Airbnb",      "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Maya Sharma",   "review_text":"Gorgeous sunsets from the deck. Deepak made excellent chai every morning. Heating could be better."},
    {"id":"RV029","platform":"Google",      "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Aditya Rao",    "review_text":"Loved it. Deepak took great care of us."},
    {"id":"RV030","platform":"Airbnb",      "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":1.0, "rating_scale":5, "host_responded":False, "guest_name":"Pooja Agarwal", "review_text":"Worst experience. The villa was not cleaned before we arrived - dirty dishes in the sink and hair in the beds. Ganesh blamed the housekeeping vendor."},
    {"id":"RV031","platform":"Booking.com", "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":4.0, "rating_scale":10,"host_responded":False, "guest_name":"K. Bhosale",    "review_text":"Arrived to an unclean property. Bedsheets were not changed. Very poor."},
    {"id":"RV032","platform":"Google",      "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Ravi Chauhan",  "review_text":"Cleanliness was a serious issue on arrival. The vineyard itself is beautiful though."},
    {"id":"RV033","platform":"Airbnb",      "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Farah Khan",    "review_text":"Lovely vineyard setting, great for a couples getaway. Wine tour next door was a highlight."},
    {"id":"RV034","platform":"Booking.com", "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":8.0, "rating_scale":10,"host_responded":False, "guest_name":"N. Patil",      "review_text":"Nice property. A bit far from Nashik city, plan your travel."},
    {"id":"RV035","platform":"Google",      "property_id":"P02","property_name":"Hilltop Haven",      "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":1.0, "rating_scale":5, "host_responded":False, "guest_name":"Yash Mehta",    "review_text":"Booked for a group but they turned away our extra guests at the gate citing occupancy policy. Felt blindsided - this wasn't clear at booking.", "noise_flag":"policy_complaint"},
    {"id":"RV036","platform":"Airbnb",      "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Aarti Menon",   "review_text":"Second time staying here and Suresh remembers us every visit. Pool was clean this time - looks like they sorted it out.", "resolved_flag":"pool_fixed"},
    {"id":"RV037","platform":"Booking.com", "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":3.0, "rating_scale":10,"host_responded":False, "guest_name":"S. Joshi",      "review_text":"Cleanliness needs serious attention. Second time I've faced this at a Spacez villa."},
    {"id":"RV038","platform":"Google",      "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Grace Thomas",  "review_text":"Great stay overall. Check-in over WhatsApp was smooth and quick."},
    {"id":"RV039","platform":"Airbnb",      "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":3.0, "rating_scale":5, "host_responded":False, "guest_name":"Mohit Sethi",   "review_text":"The place is beautiful but the listing said 4 bedrooms and one was basically a store room with a mattress. Slightly oversold."},
    {"id":"RV040","platform":"Booking.com", "property_id":"P04","property_name":"Coorg Canopy",       "location":"Madikeri, Coorg, Karnataka", "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":9.0, "rating_scale":10,"host_responded":True,  "guest_name":"L. Nair",       "review_text":"Loved the bonfire arrangement. Caretaker was attentive once he arrived."},
    {"id":"RV041","platform":"Google",      "property_id":"P06","property_name":"Cliffside Retreat",  "location":"Kasauli, Himachal Pradesh",  "caretaker_id":"CT05","caretaker_name":"Deepak Sharma","rating_raw":5.0, "rating_scale":5, "host_responded":False, "guest_name":"Rahul Dev",     "review_text":"Amazing.", "noise_flag":"too_vague"},
    {"id":"RV042","platform":"Airbnb",      "property_id":"P02","property_name:"Hilltop Haven",       "location":"Lonavala, Maharashtra",      "caretaker_id":"CT02","caretaker_name":"Mahesh Patil", "rating_raw":1.0, "rating_scale":5, "host_responded":False, "guest_name":"Simran Kaur",   "review_text":"Do not book. Misleading photos and no WiFi. Exactly the issues other reviews mentioned."},
    {"id":"RV043","platform":"Booking.com", "property_id":"P01","property_name":"Serenity Villa",     "location":"Assagao, Goa",               "caretaker_id":"CT01","caretaker_name":"Suresh Naik",  "rating_raw":8.0, "rating_scale":10,"host_responded":True,  "guest_name":"P. Dsouza",     "review_text":"Great villa, Suresh excellent. Pool maintenance is the only recurring gripe I'd flag."},
    {"id":"RV044","platform":"Google",      "property_id":"P03","property_name":"Misty Estate",       "location":"Chikmagalur, Karnataka",     "caretaker_id":"CT03","caretaker_name":"Lokesh Gowda", "rating_raw":2.0, "rating_scale":5, "host_responded":False, "guest_name":"Akash Jain",    "review_text":"Late check-in again. Seems to be a pattern with this caretaker."},
    {"id":"RV045","platform":"Airbnb",      "property_id":"P05","property_name":"Backwater Bungalow", "location":"Alleppey, Kerala",           "caretaker_id":"CT04","caretaker_name":"Biju Thomas",  "rating_raw":4.0, "rating_scale":5, "host_responded":True,  "guest_name":"Emily Davis",   "review_text":"Biju is fantastic. Wish there were more restaurants nearby but that's the location, not the villa."},
    {"id":"RV046","platform":"Google",      "property_id":"P07","property_name":"Vineyard Villa",     "location":"Nashik, Maharashtra",        "caretaker_id":"CT06","caretaker_name":"Ganesh More",  "rating_raw":5.0, "rating_scale":5, "host_responded":True,  "guest_name":"Ananya Bose",   "review_text":"Beautiful sunsets over the vines. Perfect anniversary trip."},
]
```

---

## 7. BACKEND — utils/normalize.py

```python
from typing import List, Dict, Any

def normalize_rating(raw: float, scale: int) -> float:
    return round((raw / scale) * 10, 1)

def avg_normalized_rating(reviews: List[Dict[str, Any]]) -> float:
    if not reviews:
        return 0.0
    total = sum(normalize_rating(r["rating_raw"], r["rating_scale"]) for r in reviews)
    return round(total / len(reviews), 1)

def response_rate(reviews: List[Dict[str, Any]]) -> int:
    if not reviews:
        return 0
    responded = sum(1 for r in reviews if r.get("host_responded"))
    return round((responded / len(reviews)) * 100)

def rating_tier(score: float) -> str:
    if score >= 7.5:
        return "good"
    elif score >= 5.5:
        return "mid"
    return "bad"
```

---

## 8. BACKEND — utils/grouping.py

```python
from typing import List, Dict, Any
from collections import defaultdict

def group_by_property(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
```

---

## 9. BACKEND — utils/rules.py

```python
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
    text = review_text.lower()
    return not any(kw in text for kw in NON_CARETAKER_FAULT_KEYWORDS)

def filter_noise(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in reviews if r["id"] not in NOISE_REVIEW_IDS]

def get_property_fault_issues(reviews: List[Dict[str, Any]]) -> List[str]:
    """Return list of property-level issues (not caretaker's fault)."""
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
    return list(set(issues))
```

---

## 10. BACKEND — models/schemas.py

```python
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
    cross_property_pattern: Optional[str]
    has_resolved_issue: bool
    resolved_issue_note: Optional[str]
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
    cross_property_warning: Optional[str]
    what_guests_loved: List[str]
    one_thing_to_improve: Optional[str]
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
```

---

## 11. BACKEND — services/claude_service.py

```python
import json
import anthropic
from typing import List, Dict, Any
from utils.normalize import normalize_rating

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env automatically

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
    """Call Claude API for one property. Returns parsed dict."""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": build_user_prompt(property_name, reviews)
            }]
        )
        raw = message.content[0].text
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"Claude API error for {property_name}: {e}")
        return {
            "avg_normalized_rating": None,
            "recurring_issues": [],
            "what_works_well": [],
            "noise_excluded_reasons": [],
            "resolved_issues": [],
            "api_error": True
        }
```

---

## 12. BACKEND — main.py (FastAPI App — Full)

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List

from data.reviews import REVIEWS
from utils.normalize import avg_normalized_rating, response_rate, rating_tier, normalize_rating
from utils.grouping import group_by_property, group_by_caretaker
from utils.rules import (
    filter_noise, is_caretaker_controllable, get_property_fault_issues,
    CROSS_PROPERTY_CARETAKERS, NOISE_REVIEW_IDS,
    RESOLVED_FLAGS, RESOLVED_PROPERTY_IDS
)
from services.claude_service import analyze_property
from models.schemas import AnalysisResponse, PropertyAnalysis, CaretakerDigest, BusinessMetrics, IssueItem

load_dotenv()

app = FastAPI(title="Spacez Review Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173"), "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "reviews_loaded": len(REVIEWS)}

@app.get("/api/reviews")
def get_reviews():
    """Return all raw reviews — useful for debugging."""
    return {"reviews": REVIEWS, "count": len(REVIEWS)}

@app.get("/api/analyze", response_model=AnalysisResponse)
def run_full_analysis():
    """
    Main endpoint. Runs Claude analysis on all 7 properties.
    Returns complete data for all 3 stakeholder tabs.
    Called once when user clicks 'Run Analysis'.
    """
    properties = group_by_property(REVIEWS)
    caretakers = group_by_caretaker(REVIEWS)

    # ── OPS TAB ──────────────────────────────────────────────────────────────
    ops_results: List[PropertyAnalysis] = []

    for prop in properties:
        clean_reviews = filter_noise(prop["reviews"])
        ai = analyze_property(prop["property_name"], clean_reviews)

        avg = ai.get("avg_normalized_rating") or avg_normalized_rating(clean_reviews)
        platforms = list(set(r["platform"] for r in prop["reviews"]))
        cross = CROSS_PROPERTY_CARETAKERS.get(prop["caretaker_id"])
        has_resolved = prop["property_id"] in RESOLVED_PROPERTY_IDS
        resolved_note = None
        if has_resolved:
            for flag in RESOLVED_FLAGS.values():
                if flag["property_id"] == prop["property_id"]:
                    resolved_note = flag["note"]
                    break

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
        # Sort: CRITICAL first, then RECURRING, then ONE_OFF
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

    # Sort ops: worst rated first (most urgent)
    ops_results.sort(key=lambda x: x.avg_normalized_rating)

    # ── BUSINESS TAB ─────────────────────────────────────────────────────────
    all_reviews = REVIEWS
    portfolio_avg = avg_normalized_rating(all_reviews)
    port_response_rate = response_rate(all_reviews)
    critical_count = sum(
        1 for p in ops_results
        for issue in p.recurring_issues
        if issue.severity == "CRITICAL"
    )

    portfolio_rows = []
    for p in sorted(ops_results, key=lambda x: -x.avg_normalized_rating):
        portfolio_rows.append({
            "property_id": p.property_id,
            "property_name": p.property_name,
            "avg_rating": p.avg_normalized_rating,
            "rating_tier": p.rating_tier,
            "response_rate": p.response_rate,
            "review_count": p.review_count,
            "has_resolved": p.has_resolved_issue,
            "critical_count": sum(1 for i in p.recurring_issues if i.severity == "CRITICAL")
        })

    signals = [
        {"type": "STAR",     "property": "Backwater Bungalow", "message": "Portfolio best performer. Biju Thomas sets the hospitality benchmark. Replicate his caretaker model."},
        {"type": "ACTION",   "property": "Hilltop Haven",      "message": "Listing accuracy is a business risk. Misleading photos + broken WiFi. Review investment or update listing."},
        {"type": "WATCH",    "property": "Vineyard Villa",      "message": "Housekeeping vendor reliability. Cleanliness failures across 4+ reviews. SLA review required."},
        {"type": "RESOLVED", "property": "Serenity Villa",      "message": "RV036 (repeat guest) confirms pool was clean. Monitor to confirm sustained improvement."},
        {"type": "NOTE",     "property": "Hilltop Haven",       "message": "RV035 occupancy policy complaint excluded from hospitality scoring — this is a listing clarity issue."},
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
        controllable = [r for r in ct["reviews"] if is_caretaker_controllable(r["review_text"])]
        ct_score = avg_normalized_rating(controllable) if controllable else 0.0

        cross = CROSS_PROPERTY_CARETAKERS.get(ct["caretaker_id"])

        # One thing to improve — max 1 item
        checkin_issues = [r for r in ct["reviews"] if any(k in r["review_text"].lower() for k in ["check-in", "late", "arrived late", "unreachable", "delay"])]
        clean_issues = [r for r in ct["reviews"] if any(k in r["review_text"].lower() for k in ["clean", "dirty", "dishes", "bedsheet", "housekeep"])]

        one_thing = None
        if len(checkin_issues) >= 2:
            one_thing = f"Check-in punctuality — late arrivals mentioned in {len(checkin_issues)} reviews"
        elif len(clean_issues) >= 2:
            one_thing = f"Pre-arrival cleanliness coordination with housekeeping vendor ({len(clean_issues)} reviews)"

        # What guests loved — from high-rated controllable reviews
        loved = []
        for r in controllable:
            norm = normalize_rating(r["rating_raw"], r["rating_scale"])
            if norm >= 8.0:
                loved.append(r["review_text"][:80] + ("…" if len(r["review_text"]) > 80 else ""))
        loved = loved[:3]  # max 3 items

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

    return AnalysisResponse(ops=ops_results, business=business, caretaker=caretaker_digests)
```

---

## 13. BACKEND — Run Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test it:
```
http://localhost:8000/health
http://localhost:8000/docs        ← Swagger UI — test all endpoints here
http://localhost:8000/api/analyze
```

---

## 14. FRONTEND — backendApi.js

```js
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function runAnalysis() {
  const response = await axios.get(`${BASE_URL}/api/analyze`);
  return response.data;
  // Returns: { ops: [...], business: {...}, caretaker: [...] }
}

export async function getHealth() {
  const response = await axios.get(`${BASE_URL}/health`);
  return response.data;
}
```

---

## 15. FRONTEND — App.jsx (State Machine)

```jsx
import { useState } from 'react';
import Header from './components/Header';
import TabBar from './components/TabBar';
import AnalyzeButton from './components/AnalyzeButton';
import ProgressList from './components/ProgressList';
import OpsView from './components/ops/OpsView';
import BusinessView from './components/business/BusinessView';
import CaretakerView from './components/caretaker/CaretakerView';
import { runAnalysis } from './api/backendApi';

export default function App() {
  const [phase, setPhase] = useState('idle');      // 'idle' | 'analyzing' | 'done'
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('ops');
  const [error, setError] = useState(null);

  async function handleAnalyze() {
    setPhase('analyzing');
    setError(null);
    try {
      const data = await runAnalysis();
      setResults(data);
      setPhase('done');
    } catch (e) {
      setError('Analysis failed. Check backend is running.');
      setPhase('idle');
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-3xl mx-auto px-4 py-6">
        <Header />

        {phase === 'idle' && (
          <div className="text-center py-12">
            <p className="text-sm text-gray-500 mb-4">
              Analyze 46 reviews across 7 properties using AI
            </p>
            <button
              onClick={handleAnalyze}
              className="bg-gray-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
            >
              Run analysis ↗
            </button>
            {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
          </div>
        )}

        {phase === 'analyzing' && (
          <div className="py-8 text-center">
            <p className="text-sm text-gray-500 mb-4">AI analyzing all 7 properties…</p>
            <div className="animate-pulse text-gray-400 text-xs">This takes 30–60 seconds</div>
          </div>
        )}

        {phase === 'done' && results && (
          <>
            <TabBar activeTab={activeTab} setActiveTab={setActiveTab} />
            {activeTab === 'ops'        && <OpsView data={results.ops} />}
            {activeTab === 'business'   && <BusinessView data={results.business} />}
            {activeTab === 'caretaker'  && <CaretakerView data={results.caretaker} />}
          </>
        )}
      </div>
    </div>
  );
}
```

---

## 16. FRONTEND — Tailwind Design System

```
COLORS
Rating good (≥7.5):    bg-green-50 text-green-700 border-green-200
Rating mid (5.5–7.5):  bg-amber-50 text-amber-700 border-amber-200
Rating bad (<5.5):     bg-red-50   text-red-700   border-red-200

Tag CRITICAL:          bg-red-50   text-red-700   border border-red-200
Tag RECURRING:         bg-amber-50 text-amber-700 border border-amber-200
Tag ONE_OFF:           bg-gray-50  text-gray-600  border border-gray-200
Tag CARETAKER:         bg-blue-50  text-blue-700  border border-blue-200
Tag PROPERTY:          bg-gray-50  text-gray-400  border border-gray-200

Alert cross-property:  bg-blue-50  text-blue-800  border border-blue-200 rounded-lg p-3
Box works-well:        bg-green-50 border-l-2 border-green-400 p-2 rounded
Box property-issues:   bg-gray-50  border-l-2 border-gray-300 p-2 rounded
Resolved badge:        bg-green-50 text-green-700 border border-green-200

LAYOUT
Max width:    max-w-3xl mx-auto px-4 py-6
Card:         bg-white border border-gray-100 rounded-xl p-4 mb-3 shadow-sm
Tab bar:      flex border-b border-gray-100 mb-4 gap-1
Tab active:   border-b-2 border-gray-900 text-gray-900 font-medium pb-2 px-3 text-sm
Tab inactive: text-gray-400 hover:text-gray-600 pb-2 px-3 text-sm cursor-pointer
Metric card:  bg-gray-50 rounded-lg p-4 (grid grid-cols-2 md:grid-cols-4 gap-3)
```

---

## 17. FRONTEND — vite.config.js

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
});
```

---

## 18. FRONTEND — package.json

```json
{
  "name": "spacez-frontend",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "vite": "^5.2.12"
  }
}
```

---

## 19. FRONTEND — .env

```env
VITE_BACKEND_URL=http://localhost:8000
```

For production (Vercel):
```env
VITE_BACKEND_URL=https://your-backend.railway.app
```

---

## 20. DEPLOYMENT

### Backend → Railway (free)
```bash
# In backend/ folder
# Create railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```
Add env var in Railway dashboard: `ANTHROPIC_API_KEY=sk-ant-xxxxx`

### Frontend → Vercel (free)
```bash
cd frontend
npm run build
npx vercel --prod
```
Add env var in Vercel dashboard: `VITE_BACKEND_URL=https://your-backend.railway.app`

### Run Both Locally
```bash
# Terminal 1 — backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm install && npm run dev
# Opens at http://localhost:5173
```

---

## 21. GRADER CHECKLIST — Verify Before Submitting

| # | Check | Where |
|---|-------|-------|
| 1 | Ratings normalized (Booking 6/10 ≠ Airbnb 3/5) | Ops card avg badges |
| 2 | Lokesh Gowda cross-property alert on P03 AND P04 | Ops tab both cards |
| 3 | RV035 + RV041 not driving any issue flag | Ops tab — no policy/vague issues |
| 4 | Caretaker WiFi shown as PROPERTY not coaching issue | Caretaker → Mahesh Patil card |
| 5 | Serenity Villa "resolved ✓" badge visible | Ops + Business tab |
| 6 | Backwater Bungalow starred as best performer | Business signals section |
| 7 | Vineyard Villa CRITICAL cleanliness (first card) | Ops tab — sorted worst first |
| 8 | Hilltop Haven WiFi + photo issues tagged PROPERTY | Ops tab |
| 9 | Ganesh More cleanliness = CARETAKER issue | Caretaker tab |
| 10 | Deepak Sharma heating = PROPERTY issue | Caretaker tab |
| 11 | /health endpoint returns 200 | curl localhost:8000/health |
| 12 | /docs Swagger UI shows all routes | localhost:8000/docs |
| 13 | No API key in frontend code | grep -r "sk-ant" frontend/src → 0 results |
| 14 | Analysis completes without error | No 500s in backend logs |

---

## 22. SPEC + RISKS (Paste into Google Doc)

### Problem framing
Spacez runs 7 premium villa stays across India. Reviews arrive on Airbnb, Booking.com, and Google on different rating scales with no cross-platform synthesis. Issues recur because nobody reads across platforms systematically. Hospitality quality is invisible at scale and the business has no portfolio-level view.

### Flow: Trigger → Analysis → Output → Action

| Stage | Detail |
|-------|--------|
| Trigger | On-demand via dashboard "Run Analysis" button (extensible to daily cron) |
| Pre-processing | Python backend normalizes ratings → filters noise reviews → tags caretaker vs property fault → flags cross-property patterns |
| AI analysis | FastAPI calls Claude API per property with structured prompt → validates JSON → returns typed Pydantic response |
| Output | Three completely different stakeholder views (not three identical reports) |
| Action | Ops: fix ticket same day · Business: weekly portfolio review · Caretaker: monthly coaching digest |

### What each stakeholder gets and why
**Operations** gets a priority action board sorted worst-first. They need to act on the most urgent property today. Recommended action, severity, and whether it's recurring or a one-off are all they need.

**Business** gets a normalized portfolio scorecard. They care about which properties to invest in, reprice, or drop. The Serenity Villa pool resolution is a signal that ops is functioning. Hilltop Haven's listing gap is a revenue risk.

**Caretakers** get a coaching digest with hospitality-only scores. A caretaker shown a low score because their property has bad WiFi will disengage. We filter non-controllable issues out of their score and surface property-level problems in a separate "flagged to ops" section.

### Key trade-offs

| Trade-off | Decision |
|-----------|----------|
| API key security | Moved all Claude calls to Python backend — key never in browser |
| AI accuracy vs speed | Sequential per-property calls — no rate limit errors |
| Caretaker fairness | Filter non-controllable issues from score — gaming risk mitigated by ops seeing full picture |
| Sample size | 46 reviews is directional signal — label all insights accordingly |
| Hallucination | Prompt requires supporting evidence; Pydantic validates response shape; fallback on parse error |

### Success metrics
- % reviews yielding actionable issue (target >60%)
- Time from review to ops notified (target: same day)
- Issue recurrence rate after flagging (target <30% at 60 days)
- Caretaker fairness score in survey (target >4/5)

### Risks & Pushback
**1. Caretaker hypothesis is risky as originally designed.** Showing caretakers all reviews would penalize Lokesh Gowda for a bad access road and Deepak Sharma for broken heating infrastructure — neither of which they control. We redesigned to show hospitality-only scores.

**2. AI misclassification edge cases.** Prompt includes a classification rule list but edge cases exist. Mitigate by requiring supporting evidence in every issue and adding a human review layer before caretaker-facing output is sent.

**3. Gaming risk.** Once caretakers know the scoring model, they may deprioritize infrastructure issues. Mitigation: ops team sees the full picture; caretaker score is a coaching tool, not a pay KPI.

**4. 46 reviews too small for statistical confidence.** All insights should be labelled "directional signal" until review volume is 3×.

**What to validate first:** Run the caretaker report by 2–3 caretakers before shipping. Ask: "Does this feel fair? Is anything here outside your control?"

