# 🍽️ RestaurantIQ

**AI-Powered Competitive Intelligence for Restaurants**

[![Powered by Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)](https://restaurantiq.vercel.app)

> **Give us your address. We'll give you competitive intelligence that would cost $5,000 and 2 months with a consultant.**

RestaurantIQ is an autonomous AI intelligence platform that uses Google Gemini 3's multimodal capabilities to gather, analyze, and synthesize competitive data for restaurants. No spreadsheets. No manual research. Just your location—and our AI does the rest.

---

## 🎯 The Problem We Solve

**Traditional competitive analysis:**
- ❌ Hire consultant: $5,000+
- ❌ Wait 2 months for report
- ❌ Manual data collection from dozens of sources
- ❌ Static insights, outdated by publication
- ❌ Requires structured data you don't have

**RestaurantIQ:**
- ✅ Enter your address: $0-5
- ✅ Get insights in 5 minutes
- ✅ AI autonomously gathers data from Google Maps, Instagram, reviews, menus
- ✅ Dynamic, real-time intelligence
- ✅ Works with minimal input—we fill the gaps

---

## 🌟 What Makes RestaurantIQ Different

### **1. Zero Friction Input**
**You provide (optionally):**
- 📍 Your address
- 📷 Your menu (photo, PDF, or URL)
- 📊 Sales data (CSV, if available)
- 📱 Your social media handles

**We fill the rest automatically:**
- 🔍 Discover competitors in your area
- 🌐 Scrape their menus, prices, photos
- ⭐ Gather reviews, ratings, sentiment
- 📸 Analyze their social media aesthetics
- 🏙️ Understand your neighborhood demographics

### **2. True Multimodal Intelligence**

RestaurantIQ doesn't just read text. We analyze:

| Data Type | What We Extract | Example Insight |
|-----------|----------------|-----------------|
| **📸 Dish Photos** | Presentation quality, portion size, plating style | "Your pasta portions appear 20% smaller than Competitor A based on customer photos" |
| **🍽️ Menu Images** | Items, prices, categories, promotions | "3/5 competitors offer breakfast; you don't—potential gap" |
| **🏪 Ambiance Photos** | Decor, lighting, atmosphere | "Your interior is darker than area average; customers associate this with romantic dining vs casual" |
| **📱 Social Posts** | Visual style, engagement, posting frequency | "Competitor B uses warm filters with 2.3x higher engagement than your current aesthetic" |
| **⭐ Customer Photos** | Actual served dishes vs menu photos | "Your burger photos show 15% smaller patties than advertised—consistency issue" |
| **📍 Location Data** | Foot traffic, neighborhood type, nearby businesses | "You're in a university zone—student discounts could increase volume 30%" |

### **3. Autonomous Intelligence Gathering (The "Scout" Agent)**

**Traditional tools:** You input data manually.

**RestaurantIQ:** Our AI autonomously discovers and enriches data.
```python
# You give us this:
{
    "address": "Calle 5 #23-45, Bogotá, Colombia"
}

# Our Scout Agent does this:
1. Geocodes your location
2. Searches Google Maps for "restaurants" within 500m
3. Identifies 7 potential competitors
4. For each competitor:
   - Scrapes Google Business profile
   - Downloads menu photos (if available)
   - Extracts contact info, hours, ratings
   - Finds Instagram/Facebook handles
   - Downloads recent social media posts
   - Scrapes Yelp/TripAdvisor reviews
   - Analyzes customer-uploaded photos
5. Analyzes neighborhood:
   - Nearby businesses (offices? universities? residential?)
   - Foot traffic patterns
   - Demographic indicators
6. Cross-references data sources
7. Removes duplicates (same place, different names)
8. Validates data quality
9. Generates comprehensive intelligence report
```

**All of this happens automatically.** You just wait 3-5 minutes.

---

## 🧠 How Gemini 3 Powers Every Feature

RestaurantIQ is built on three advanced agentic patterns that showcase Gemini 3's capabilities:

### **1. Marathon Agent Pattern** - Autonomous Multi-Step Workflows

Traditional analysis is sequential. RestaurantIQ's Marathon Agent orchestrates complex, long-running intelligence pipelines with checkpoints and resilience.
```python
# The Marathon Agent coordinates 7 parallel intelligence streams:

Pipeline:
1. Location Intelligence
   └─> Geocode → Find competitors → Neighborhood analysis
   
2. Menu Intelligence  
   └─> Extract yours → Scrape competitors → Price comparison
   
3. Visual Intelligence
   └─> Analyze dish photos → Compare presentation → Quality scores
   
4. Social Intelligence
   └─> Download posts → Aesthetic analysis → Engagement patterns
   
5. Review Intelligence
   └─> Scrape reviews → Sentiment analysis → Theme extraction
   
6. Business Intelligence
   └─> BCG classification → Sales forecasting → Gap analysis
   
7. Campaign Intelligence
   └─> Synthesize all data → Generate targeted campaigns

Each stream runs independently with fault tolerance.
If one fails, others continue. All results merge into unified insights.
```

**Example Execution:**
```python
orchestrator = IntelligenceOrchestrator()

result = await orchestrator.run_full_pipeline(
    location="Calle 85 #15-32, Bogotá",
    menu_photo="data:image/jpeg;base64,/9j/4AAQ...",  # Optional
    sales_csv="sales_2024.csv",  # Optional
    social_handles={"instagram": "@mi_restaurante"},  # Optional
    search_radius_meters=500,
    thinking_level="DEEP"
)

# Returns after ~3-5 minutes with complete intelligence
```

### **2. Vibe Engineering Pattern** - Self-Verification & Improvement

RestaurantIQ doesn't just analyze—it double-checks itself.

**The Verification Loop:**
1. **Generate Initial Analysis** (e.g., "Competitor prices are 10% lower")
2. **Self-Verify**: "Do I have enough data? Are sources reliable?"
3. **Cross-Reference**: Check claim against multiple sources
4. **Detect Contradictions**: Flag if data sources conflict
5. **Confidence Score**: Assign certainty to each insight (0-100%)
6. **Re-analyze** if confidence < 80%
7. **Final Output** with uncertainty quantification

**Example:**
```json
{
  "insight": "Your tacos are 15% more expensive than area average",
  "confidence": 87,
  "sources": [
    "Analyzed 5 competitor menus",
    "Cross-referenced Google Maps pricing",
    "Verified against 23 customer reviews mentioning price"
  ],
  "verification_status": "VERIFIED",
  "contradictions": null
}
```

### **3. Context Loop** - Temporal Intelligence

RestaurantIQ doesn't just see static data—it tracks changes over time.

**Example:**
```
Gemini discovers two menus for "Taquería El Primo":
- Menu from 2023: Tacos al Pastor $60 MXN
- Menu from 2025: Tacos al Pastor $85 MXN

Context Loop Analysis:
"Competitor has increased prices 42% in 2 years, likely due to inflation. 
Your prices ($75) are now mid-range instead of premium. Consider positioning 
change or price adjustment to maintain margin."
```

---

## 🔥 Signature Features

### **A. Neighborhood Sentiment Analysis**

RestaurantIQ doesn't just find competitors—it understands your market.

**The Scout Agent analyzes:**
- **Nearby Businesses**: Are you surrounded by offices (lunch rush) or nightclubs (late-night demand)?
- **Demographics**: University students vs. corporate professionals vs. families
- **Foot Traffic**: Peak hours based on location type
- **Seasonal Patterns**: Tourist area vs. residential neighborhood

**Output:**
```json
{
  "neighborhood_type": "University District",
  "primary_demographic": "Students (18-25)",
  "peak_hours": ["12:00-14:00", "18:00-20:00"],
  "average_order_value": "$8-12",
  "price_sensitivity": "HIGH",
  "opportunity": "Student discount programs could increase volume 30-40%",
  "competitive_positioning": "You're premium-priced for a student area",
  "recommendation": "Consider value combos or student loyalty program"
}
```

### **B. Visual Gap Analysis**

Gemini 3's multimodal vision compares your visual presence against competitors.

**What it analyzes:**

1. **Dish Photography Quality**
```
Your Burger:
- Lighting: Natural (Score: 7/10)
- Composition: Centered (Score: 6/10)
- Color Saturation: Low (Score: 5/10)
- Professional Score: 6.0/10

Competitor Average:
- Lighting: Studio (Score: 8.5/10)
- Composition: Rule of thirds (Score: 8/10)  
- Color Saturation: Enhanced (Score: 9/10)
- Professional Score: 8.5/10

Actionable Insight:
"Your photos are under-saturated. Customers perceive this as less appetizing.
Consider increasing color vibrancy by 20-30% or investing in professional
food photography. Expected engagement increase: +45%."
```

2. **Social Media Aesthetic**
```
Your Instagram Feed:
- Dominant Colors: Browns, grays
- Filter Style: None/minimal
- Posting Pattern: Inconsistent (2-3x per week)
- Engagement Rate: 1.8%

Top Competitor Feed:
- Dominant Colors: Warm tones, reds, yellows
- Filter Style: Consistent warm filter
- Posting Pattern: Daily at 11 AM
- Engagement Rate: 4.2%

Actionable Insight:
"Adopt a warm color palette and consistent posting schedule.
Based on competitor analysis, switching to daily posts at 11 AM
could increase engagement by 2.3x."
```

3. **Menu Design Comparison**
```
Your Menu:
- Layout: Text-heavy, minimal images
- Readability: 6/10
- Visual Hierarchy: Unclear
- Professional Score: 5.5/10

Best-in-Class Competitor:
- Layout: Image-focused, scannable sections
- Readability: 9/10
- Visual Hierarchy: Clear categories, highlighted specials
- Professional Score: 8.8/10

Actionable Insight:
"Your menu is difficult to scan. Consider adding photos to top 5 items
and using visual separators between categories. Estimated order speed
improvement: 25%."
```

### **C. Competitive Positioning Matrix**

RestaurantIQ maps you and your competitors on multiple dimensions.

**2D Positioning Map:**
```
          Visual Quality (Gemini Score)
                    ↑
            10 |           * Competitor C
               |
             8 |  * Competitor A    * Competitor B
               |        
             6 |      YOU ●
               |
             4 |  * Competitor D
               |
             2 |
               └─────────────────────────────→
                2    4    6    8    10    12
                    Average Price ($)
                    
Strategic Insight:
"You're positioned as 'mid-price, mid-quality'. Competitors A and B
are winning the premium segment. Opportunity: Either improve visual
quality to compete premium, or lower prices to dominate value segment."
```

### **D. Price Elasticity Intelligence**

RestaurantIQ analyzes not just competitor prices, but customer price sensitivity.
```json
{
  "your_price": "$12",
  "competitor_range": "$8 - $15",
  "market_position": "Upper-mid",
  "customer_sentiment": {
    "price_mentions_in_reviews": 47,
    "negative_price_sentiment": 23,
    "positive_price_sentiment": 12,
    "neutral": 12,
    "net_sentiment": -11,
    "interpretation": "Customers perceive your pricing as slightly high for perceived value"
  },
  "elasticity_estimate": {
    "price_decrease_10_percent": "+18% volume (expected)",
    "price_increase_10_percent": "-22% volume (expected)"
  },
  "recommendation": "Current pricing is in elastic range. Consider value adds (sides, combos) instead of price cuts to maintain margin while improving perceived value."
}
```

### **E. BCG Matrix with Multimodal Enhancement**

Traditional BCG uses sales data. RestaurantIQ combines sales + visual quality + customer sentiment.

**Enhanced BCG Classification:**

| Item | Sales Growth | Market Share | Visual Score | Sentiment | Final Category | Insight |
|------|-------------|--------------|--------------|-----------|----------------|---------|
| Burger Clásico | +15% | High | 6.5/10 | +0.3 | **STAR⭐** | "High demand despite mediocre photos—huge opportunity. Improve photography for 20-30% boost." |
| Caesar Salad | +2% | High | 8.2/10 | +0.7 | **CASH COW💰** | "Beautiful presentation, stable sales. Maintain quality, consider premium version." |
| Fish Tacos | +25% | Low | 7.8/10 | +0.5 | **QUESTION MARK❓** | "Growing fast but low share. Visual quality is good—invest in promotion." |
| Quesadilla | -8% | Low | 5.1/10 | -0.2 | **DOG🐕** | "Declining sales, poor presentation, negative reviews. Consider removal or complete revamp." |

### **F. Campaign Generation with Full Context**

RestaurantIQ generates campaigns that leverage ALL intelligence gathered.

**Example Campaign (Generated from Full Analysis):**
```json
{
  "campaign_id": "CAMP_001",
  "title": "Student Tuesday Takeover",
  "objective": "Penetrate university demographic identified in neighborhood analysis",
  
  "target_audience": {
    "primary": "University students (18-25)",
    "secondary": "Young professionals in surrounding area",
    "psychographic": "Price-sensitive, social media active, value-oriented"
  },
  
  "strategy": {
    "hook": "Based on visual gap analysis, your competitors use warm, vibrant imagery. This campaign adopts that aesthetic while highlighting value.",
    "differentiation": "Only restaurant in area offering student discount + Instagram-worthy presentation",
    "neighborhood_context": "University district with peak traffic 12-2pm and 6-8pm"
  },
  
  "creative": {
    "visual_direction": "Use warm filters, overhead shots, bright colors. Reference Competitor B's successful aesthetic.",
    "copy": {
      "instagram": "📚 Studying hard? Eat well for less. Every Tuesday: 20% off with student ID + Free upgrade to combo. Tag us for a chance to win a free week of lunches! 🌮📖 #StudentTuesday #FoodieLife #[YourRestaurant]",
      "email_subject": "Your Tuesday Just Got Tastier (+ Cheaper)",
      "email_body": "Hey [Name], We know student budgets are tight...",
      "facebook": "Attention students! 📣 Your new Tuesday tradition..."
    }
  },
  
  "execution": {
    "channels": ["Instagram", "Facebook", "TikTok", "Campus flyers"],
    "timing": "Launch 2 weeks before midterms (high stress = comfort food demand)",
    "budget": "$200-300 (mostly organic + $100 Instagram ads)",
    "success_metrics": ["20% student traffic increase", "30+ Instagram mentions", "+500 followers"]
  },
  
  "competitive_intelligence": {
    "gap_exploited": "None of your competitors target students specifically",
    "aesthetic_shift": "Adopting Competitor B's warm aesthetic that drives 2.3x engagement",
    "pricing_context": "20% discount brings you to $9.60, below competitor average of $10.20"
  },
  
  "expected_impact": {
    "new_customers": "40-60 students per week",
    "revenue_lift": "+$800-1200 weekly",
    "social_media_growth": "+300-500 followers",
    "data_collection": "Build student database for future campaigns"
  },
  
  "gemini_reasoning": [
    "Identified university district in neighborhood analysis",
    "Detected no competitors offering student programs (gap)",
    "Visual analysis showed warm aesthetic outperforms by 2.3x",
    "Price sensitivity analysis recommended discount vs premium",
    "Timing optimized based on academic calendar + stress patterns",
    "Multi-source verification: Google Maps, Instagram, review sentiment"
  ]
}
```

**Why This is Different:**
- 🧠 Not generic template—built from YOUR specific competitive intelligence
- 📊 Data-driven every step (neighborhood type, visual gaps, pricing context)
- 🎯 Exploits actual competitive gaps discovered by AI
- 📸 Includes actionable creative direction based on competitor analysis
- 💰 ROI estimated from real market data, not guesswork

---

## 🏗️ Technical Architecture

### **System Overview**
```
┌────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│  📍 Address  📷 Menu  📊 Sales  📱 Socials  (ALL OPTIONAL)      │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE ORCHESTRATOR                    │
│                    (Marathon Agent Pattern)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Location Intel    (Scout Agent)                      │  │
│  │     - Geocode location                                   │  │
│  │     - Find competitors (Google Places API)               │  │
│  │     - Neighborhood demographic analysis                  │  │
│  │                                                           │  │
│  │  2. Data Enrichment    (Autonomous Gathering)            │  │
│  │     - Scrape competitor Google Business                  │  │
│  │     - Discover social media handles                      │  │
│  │     - Download menus, photos, reviews                    │  │
│  │     - Extract contact info, hours, ratings               │  │
│  │                                                           │  │
│  │  3. Multimodal Analysis (Gemini 3 Vision)                │  │
│  │     - Menu extraction (yours + competitors)              │  │
│  │     - Dish photo quality scoring                         │  │
│  │     - Ambiance analysis                                  │  │
│  │     - Social media aesthetic comparison                  │  │
│  │     - Customer photo analysis                            │  │
│  │                                                           │  │
│  │  4. Competitive Intelligence (Deep Analysis)             │  │
│  │     - Price positioning matrix                           │  │
│  │     - Visual gap analysis                                │  │
│  │     - Sentiment analysis (text + images)                 │  │
│  │     - Market share estimation                            │  │
│  │     - Trend detection (temporal context)                 │  │
│  │                                                           │  │
│  │  5. Business Analytics (ML + AI)                         │  │
│  │     - BCG classification (enhanced w/ multimodal)        │  │
│  │     - Sales forecasting (if data available)              │  │
│  │     - Price elasticity estimation                        │  │
│  │     - Customer LTV modeling                              │  │
│  │                                                           │  │
│  │  6. Verification Layer (Vibe Engineering)                │  │
│  │     - Cross-reference data sources                       │  │
│  │     - Detect contradictions                              │  │
│  │     - Assign confidence scores                           │  │
│  │     - Flag low-quality insights                          │  │
│  │                                                           │  │
│  │  7. Campaign Generation (Strategic AI)                   │  │
│  │     - Synthesize all intelligence                        │  │
│  │     - Exploit competitive gaps                           │  │
│  │     - Generate 3-5 targeted campaigns                    │  │
│  │     - Provide creative + execution plan                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE REPORT                         │
│  📊 Competitive Landscape  📸 Visual Analysis  💰 Pricing       │
│  🎯 BCG Matrix  📈 Forecasts  📢 Campaigns  🧠 Gemini Insights  │
└────────────────────────────────────────────────────────────────┘
```

### **Backend Architecture**
```python
backend/
├── app/
│   ├── core/
│   │   ├── config.py              # Environment & API keys
│   │   ├── logging.py             # Structured logging
│   │   └── security.py            # Rate limiting, CORS
│   │
│   ├── services/
│   │   ├── intelligence/          # 🆕 Core intelligence layer
│   │   │   ├── scout_agent.py              # Location + competitor discovery
│   │   │   ├── data_enrichment.py          # Scraping + data gathering
│   │   │   ├── multimodal_analyzer.py      # Gemini Vision analysis
│   │   │   ├── competitive_intel.py        # Price, positioning, gaps
│   │   │   ├── visual_gap_analyzer.py      # Social media aesthetic comparison
│   │   │   ├── neighborhood_analyzer.py    # 🆕 Demographic + sentiment analysis
│   │   │   ├── context_loop.py             # 🆕 Temporal intelligence
│   │   │   ├── verification_agent.py       # Self-checking + confidence
│   │   │   └── orchestrator.py             # Marathon Agent coordinator
│   │   │
│   │   ├── gemini/                # Gemini 3 integration
│   │   │   ├── base_agent.py               # Retry, rate limit, caching
│   │   │   ├── vision_agent.py             # Multimodal processing
│   │   │   ├── reasoning_agent.py          # Deep analysis & strategy
│   │   │   └── function_calling.py         # Tool use for data gathering
│   │   │
│   │   ├── analytics/             # Business intelligence
│   │   │   ├── bcg_classifier.py           # Enhanced BCG matrix
│   │   │   ├── sales_predictor.py          # Forecasting
│   │   │   ├── price_analyzer.py           # Elasticity estimation
│   │   │   └── sentiment_analyzer.py       # Review + image sentiment
│   │   │
│   │   └── campaign/              # Marketing generation
│   │       ├── campaign_generator.py       # AI campaign creation
│   │       ├── creative_director.py        # Visual strategy
│   │       └── audience_profiler.py        # Target demographic
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── intelligence.py             # Main analysis endpoints
│   │   │   ├── scout.py                    # Location search
│   │   │   ├── upload.py                   # File uploads
│   │   │   └── websocket.py                # 🆕 Real-time progress
│   │   │
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── models/                    # SQLAlchemy ORM
│   │   ├── restaurant.py
│   │   ├── competitor.py          # 🆕 Competitor data
│   │   ├── intelligence_session.py # 🆕 Analysis sessions
│   │   ├── visual_analysis.py      # 🆕 Image insights
│   │   └── neighborhood.py         # 🆕 Location context
│   │
│   └── schemas/                   # Pydantic validation
│       ├── intelligence.py         # Intelligence report schemas
│       ├── competitor.py
│       └── campaign.py
│
├── tests/
│   ├── test_scout_agent.py
│   ├── test_multimodal.py
│   └── test_verification.py
│
└── requirements.txt
```

### **Frontend Architecture**
```typescript
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                      # Landing page
│   │   ├── layout.tsx                    # Root layout
│   │   │
│   │   ├── setup/
│   │   │   └── page.tsx                  # 🆕 Intelligence setup form
│   │   │                                      (address, optional uploads)
│   │   │
│   │   └── intelligence/
│   │       └── [sessionId]/
│   │           ├── layout.tsx            # Dashboard layout with tabs
│   │           ├── page.tsx              # Overview/summary
│   │           ├── competitors/page.tsx  # 🆕 Competitor landscape
│   │           ├── visual/page.tsx       # 🆕 Visual gap analysis
│   │           ├── neighborhood/page.tsx # 🆕 Location insights
│   │           ├── bcg/page.tsx          # BCG matrix
│   │           ├── pricing/page.tsx      # 🆕 Price positioning
│   │           ├── campaigns/page.tsx    # Generated campaigns
│   │           └── insights/page.tsx     # 🆕 Gemini reasoning traces
│   │
│   ├── components/
│   │   ├── intelligence/
│   │   │   ├── CompetitorMap.tsx         # 🆕 Interactive map
│   │   │   ├── VisualComparison.tsx      # 🆕 Side-by-side photo analysis
│   │   │   ├── NeighborhoodCard.tsx      # 🆕 Demographic insights
│   │   │   ├── PositioningMatrix.tsx     # 🆕 2D competitive map
│   │   │   ├── BCGScatterPlot.tsx
│   │   │   ├── CampaignCard.tsx
│   │   │   └── InsightTrace.tsx          # 🆕 Gemini reasoning viewer
│   │   │
│   │   ├── upload/
│   │   │   ├── SetupWizard.tsx           # 🆕 Multi-step input
│   │   │   ├── LocationInput.tsx         # 🆕 Address autocomplete
│   │   │   ├── OptionalUploads.tsx
│   │   │   └── ProgressTracker.tsx       # 🆕 Real-time pipeline status
│   │   │
│   │   └── ui/                           # shadcn/ui components
│   │
│   ├── lib/
│   │   ├── api.ts                        # API client
│   │   ├── websocket.ts                  # 🆕 WebSocket for progress
│   │   └── types.ts                      # TypeScript interfaces
│   │
│   └── hooks/
│       ├── useIntelligence.ts            # Fetch intelligence data
│       ├── useWebSocket.ts               # 🆕 Real-time updates
│       └── useCompetitors.ts             # 🆕 Competitor data hook
│
└── package.json
```

---

## 🚀 Quick Start

### **Option 1: One-Click Demo (Recommended)**
```bash
# Visit live demo with pre-loaded data
https://restaurantiq.vercel.app/demo

# Try with sample restaurant:
Location: "Calle 85 #15-32, Bogotá, Colombia"
# All data auto-discovered. Just watch the magic happen.
```

### **Option 2: Docker (Production)**
```bash
git clone https://github.com/DuqueOM/RestaurantIQ.git
cd RestaurantIQ

# Set your API keys
cp .env.example .env
# Edit .env:
#   GEMINI_API_KEY=your_key
#   GOOGLE_PLACES_API_KEY=your_key (optional but recommended)

docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Option 3: Local Development**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Access at http://localhost:3000
```

---

## 📊 How It Works: A Complete Example

### **Input (Minimal)**
```json
{
  "location": "Calle 5 #23-45, Bogotá, Colombia"
}
```

### **What Happens (Autonomous)**

**Phase 1: Location Intelligence (30 seconds)**
```
[Scout Agent activates]
✓ Geocoded: 4.6097° N, 74.0817° W
✓ Neighborhood: Zona Rosa (Commercial/Entertainment)
✓ Nearby: Universities (2), Office Buildings (12), Hotels (5)
✓ Primary Demographic: Young professionals (25-40)
✓ Peak Hours: 12:00-14:00 (lunch), 19:00-23:00 (dinner/drinks)
✓ Foot Traffic: High (entertainment district)
```

**Phase 2: Competitor Discovery (60 seconds)**
```
[Scout Agent searches]
✓ Found 8 restaurants within 500m
✓ Filtering to direct competitors (similar cuisine/price)
✓ Identified 5 competitors:
  1. Taquería El Charro (4.2★, 340 reviews)
  2. Burrito Loco (4.0★, 180 reviews)
  3. La Fogata (4.5★, 520 reviews)
  4. Tacos & Más (3.8★, 95 reviews)
  5. El Rincón Mexicano (4.3★, 280 reviews)
```

**Phase 3: Data Enrichment (90 seconds)**
```
[Data Enrichment Agent scrapes]
For each competitor:
  ✓ Google Business: Address, hours, phone, website
  ✓ Menu: 23 photos downloaded, prices extracted
  ✓ Photos: 47 dish photos, 12 interior photos
  ✓ Reviews: 340 reviews scraped, sentiment analyzed
  ✓ Social: Instagram found (@taqueriaelcharro), 3.2k followers
  ✓ Recent Posts: 15 posts downloaded, engagement analyzed
```

**Phase 4: Multimodal Analysis (120 seconds)**
```
[Gemini Vision analyzes]
✓ Menu extraction: 18 items identified across 5 competitors
✓ Dish quality scores:
  - Your: 6.5/10 avg (if provided)
  - Competitor avg: 7.8/10
  - Gap: -1.3 points
✓ Social media aesthetic:
  - Your feed: Minimal, dark tones
  - Top competitor: Warm filters, vibrant colors
  - Engagement gap: 2.3x lower
✓ Customer photos analyzed:
  - Portion size perception
  - Presentation consistency
  - Quality vs. price expectations
```

**Phase 5: Competitive Intelligence (60 seconds)**
```
[Competitive Intel Agent synthesizes]
✓ Price Positioning:
  - Your avg: $11.50
  - Market avg: $10.20
  - Position: Upper-mid (+12.7%)
  
✓ Visual Gap:
  - Photography quality: Below average
  - Social engagement: 42% of benchmark
  - Opportunity: +$800/month with better visuals
  
✓ Market Gaps:
  - Breakfast: Only 1/5 competitors offer
  - Student discounts: None found
  - Delivery optimization: 3/5 use better packaging
```

**Phase 6: BCG + Forecasting (30 seconds)**
```
[Analytics Engine runs]
✓ BCG Classification (enhanced w/ visual + sentiment):
  - Stars: Tacos al Pastor (high sales, great visuals)
  - Cash Cows: Quesadillas (steady sales, easy to make)
  - Question Marks: Breakfast Burrito (new, promising)
  - Dogs: Fish Tacos (declining, poor reviews)
  
✓ Sales Forecast (if data provided):
  - Next 30 days: +12% growth expected
  - Confidence: 78%
```

**Phase 7: Campaign Generation (45 seconds)**
```
[Campaign Generator creates]
✓ Generated 3 campaigns:

Campaign 1: "Breakfast Revolution"
  - Exploit gap: Only 1 competitor has breakfast
  - Target: Office workers in area
  - Creative: "Desayuno Listo en 5 Minutos"
  - Expected ROI: +$600/week
  
Campaign 2: "Visual Upgrade Challenge"
  - Fix gap: Improve social media aesthetic
  - Adopt warm filter strategy (competitor best practice)
  - Expected: +2.3x engagement
  
Campaign 3: "Student Taco Tuesday"
  - Target: Universities nearby (gap - no one targets students)
  - Offer: 20% off with student ID
  - Expected: +40 new customers/week
```

**Phase 8: Verification (20 seconds)**
```
[Verification Agent checks]
✓ Cross-referenced 3+ sources for each insight
✓ Confidence scores assigned (60-95%)
✓ No contradictions detected
✓ All claims verified
✓ Ready for delivery
```

### **Output (Comprehensive Intelligence Report)**

Delivered in 5-6 minutes with:
- 📊 Executive Summary (1-page)
- 🗺️ Competitive Landscape Map
- 📸 Visual Gap Analysis (side-by-side comparisons)
- 💰 Price Positioning Matrix
- 🎯 Enhanced BCG Matrix
- 📈 Sales Forecasts (if data provided)
- 📢 3 Campaign Plans (ready to execute)
- 🧠 Gemini Reasoning Traces (full transparency)
- 🔍 Confidence Scores (uncertainty quantification)

**Total Cost: $3-5 in API calls**
**Traditional Equivalent: $5,000 + 2 months**

---

## 🎯 Use Cases

### **1. New Restaurant Opening**
*"I have a location but no idea who I'm competing against."*

**Input:** Just your address.

**RestaurantIQ delivers:**
- Complete competitive landscape
- Neighborhood demographic profile
- Pricing recommendations
- Visual strategy (what aesthetic works in your area)
- Launch campaign ideas

### **2. Struggling Existing Restaurant**
*"Sales are down but I don't know why."*

**Input:** Address + sales data (optional: menu, social media).

**RestaurantIQ discovers:**
- Competitors who are winning (and why)
- Where you're overpriced or underpriced
- Visual quality gaps hurting you
- Menu items to kill/promote
- Specific actions to take

### **3. Marketing Agency / Consultant**
*"I need competitive analysis for 10 restaurant clients."*

**Input:** 10 addresses.

**RestaurantIQ generates:**
- 10 comprehensive reports in 1 hour
- Cost: $30-50 vs. weeks of manual work
- Professional, data-backed deliverables
- White-label ready

### **4. Investor Due Diligence**
*"Should I invest in this restaurant?"*

**Input:** Target restaurant address.

**RestaurantIQ provides:**
- Competitive moat analysis
- Market saturation assessment
- Visual differentiation analysis
- Pricing power evaluation
- Growth opportunity identification

---

## 🔬 Technical Deep Dive

### **Scout Agent Implementation**
```python
# backend/app/services/intelligence/scout_agent.py

class ScoutAgent:
    """
    Autonomous agent that discovers and enriches competitive data.
    Implements Marathon Agent pattern for resilient long-running tasks.
    """
    
    def __init__(self, gemini_agent, places_client, scraper):
        self.gemini = gemini_agent
        self.places = places_client
        self.scraper = scraper
        self.logger = get_logger(__name__)
    
    async def discover_competitive_landscape(
        self, 
        location: str,
        search_radius_meters: int = 500,
        max_competitors: int = 5
    ) -> CompetitiveLandscape:
        """
        Full autonomous competitive intelligence pipeline.
        
        Args:
            location: Address or lat/lng
            search_radius_meters: How far to search
            max_competitors: Max competitors to analyze
            
        Returns:
            Complete competitive landscape with enriched data
        """
        
        # Step 1: Geocode & Neighborhood Analysis
        self.logger.info("Starting location intelligence", location=location)
        
        coords = await self._geocode(location)
        neighborhood = await self._analyze_neighborhood(coords)
        
        # Step 2: Discover Competitors
        self.logger.info("Discovering competitors", radius=search_radius_meters)
        
        competitors_raw = await self.places.nearby_search(
            location=coords,
            radius=search_radius_meters,
            type="restaurant"
        )
        
        # Filter to direct competitors (Gemini decides)
        competitors = await self._filter_relevant_competitors(
            candidates=competitors_raw,
            user_type="Mexican restaurant",  # Could be auto-detected from menu
            max_results=max_competitors
        )
        
        # Step 3: Enrich Each Competitor (parallel)
        self.logger.info("Enriching competitor data", count=len(competitors))
        
        enriched = await asyncio.gather(*[
            self._enrich_competitor(comp) 
            for comp in competitors
        ])
        
        # Step 4: Competitive Analysis
        landscape = CompetitiveLandscape(
            your_location=coords,
            neighborhood=neighborhood,
            competitors=enriched,
            competitive_insights=await self._generate_insights(enriched)
        )
        
        return landscape
    
    async def _analyze_neighborhood(self, coords: LatLng) -> NeighborhoodProfile:
        """
        Use Gemini to understand neighborhood from Google Places data.
        """
        # Get nearby places of all types
        nearby = await self.places.nearby_search(
            location=coords,
            radius=500,
            type=None  # All types
        )
        
        # Gemini analyzes what kind of area this is
        prompt = f"""
        Analyze this neighborhood based on nearby businesses:
        
        {json.dumps([p.type for p in nearby], indent=2)}
        
        Determine:
        1. Neighborhood type (residential, commercial, university, tourist, etc.)
        2. Primary demographic (age, income, lifestyle)
        3. Peak hours (when is foot traffic highest?)
        4. Price sensitivity (high/medium/low)
        5. Dining preferences (quick lunch, sit-down dinner, late-night, etc.)
        
        Return structured JSON.
        """
        
        analysis = await self.gemini.generate_structured(
            prompt=prompt,
            response_schema=NeighborhoodProfile
        )
        
        return analysis
    
    async def _enrich_competitor(self, competitor: Place) -> EnrichedCompetitor:
        """
        Gather all possible data about a competitor.
        """
        enriched = EnrichedCompetitor(
            name=competitor.name,
            address=competitor.address,
            location=competitor.location
        )
        
        # Google Business data
        enriched.rating = competitor.rating
        enriched.review_count = competitor.user_ratings_total
        enriched.price_level = competitor.price_level
        
        # Scrape website if available
        if competitor.website:
            try:
                website_data = await self.scraper.scrape_website(competitor.website)
                enriched.menu_items = website_data.menu
                enriched.menu_photos = website_data.photos
            except Exception as e:
                self.logger.warning("Website scraping failed", url=competitor.website, error=str(e))
        
        # Discover social media (Gemini generates search queries)
        social_queries = await self.gemini.generate_search_queries(
            business_name=competitor.name,
            location=competitor.address
        )
        
        for query in social_queries:
            social = await self._search_social_media(query)
            if social:
                enriched.social_handles.update(social)
        
        # Download social media content
        if "instagram" in enriched.social_handles:
            try:
                posts = await self.scraper.get_instagram_posts(
                    handle=enriched.social_handles["instagram"],
                    limit=15
                )
                enriched.social_posts = posts
            except Exception as e:
                self.logger.warning("Instagram scraping failed", error=str(e))
        
        # Scrape reviews
        reviews = await self.scraper.get_google_reviews(
            place_id=competitor.place_id,
            limit=50
        )
        enriched.reviews = reviews
        
        # Download photos from Google
        enriched.google_photos = await self._download_place_photos(competitor.place_id)
        
        return enriched
    
    async def _filter_relevant_competitors(
        self, 
        candidates: List[Place],
        user_type: str,
        max_results: int
    ) -> List[Place]:
        """
        Use Gemini to identify true competitors (not just nearby restaurants).
        """
        prompt = f"""
        The user is a {user_type}.
        
        Which of these nearby restaurants are direct competitors?
        
        Candidates:
        {json.dumps([{"name": p.name, "types": p.types, "price": p.price_level} for p in candidates], indent=2)}
        
        Return the {max_results} most relevant competitors ranked by:
        1. Similar cuisine type
        2. Similar price point  
        3. Similar target demographic
        
        Return JSON array of place names.
        """
        
        selected_names = await self.gemini.generate_structured(
            prompt=prompt,
            response_schema=List[str]
        )
        
        return [c for c in candidates if c.name in selected_names][:max_results]
```

### **Visual Gap Analysis**
```python
# backend/app/services/intelligence/visual_gap_analyzer.py

class VisualGapAnalyzer:
    """
    Compares visual aesthetics across restaurants using Gemini Vision.
    """
    
    async def analyze_visual_competitive_position(
        self,
        your_photos: List[Image],
        competitor_photos: Dict[str, List[Image]]
    ) -> VisualGapReport:
        """
        Deep visual analysis comparing your imagery to competitors.
        """
        
        # 1. Analyze your photos
        your_analysis = await self._batch_analyze_images(
            images=your_photos,
            analysis_type="restaurant_dishes"
        )
        
        # 2. Analyze each competitor
        competitor_analyses = {}
        for comp_name, photos in competitor_photos.items():
            competitor_analyses[comp_name] = await self._batch_analyze_images(
                images=photos,
                analysis_type="restaurant_dishes"
            )
        
        # 3. Gemini compares and identifies gaps
        prompt = f"""
        You are a professional food photographer and marketing consultant.
        
        YOUR PHOTOS:
        {json.dumps(your_analysis, indent=2)}
        
        COMPETITOR PHOTOS:
        {json.dumps(competitor_analyses, indent=2)}
        
        Provide detailed visual gap analysis:
        
        1. LIGHTING:
           - Your approach vs competitors
           - What's working / not working
           - Specific recommendation
           
        2. COMPOSITION:
           - Your framing vs competitors
           - Best practices you're missing
           - Specific recommendation
           
        3. COLOR & SATURATION:
           - Your color palette vs competitors
           - Engagement correlation
           - Specific recommendation
           
        4. STYLING & PLATING:
           - Your presentation vs competitors
           - Perceived quality gap
           - Specific recommendation
           
        5. OVERALL AESTHETIC:
           - Describe your current vibe
           - Describe winning competitor vibe
           - Strategic shift recommendation
           
        For each insight, provide:
        - Current state (1-10 score)
        - Best-in-class benchmark (1-10 score)
        - Gap size
        - Actionable fix (specific steps)
        - Expected impact (% engagement increase)
        
        Return structured JSON.
        """
        
        gap_analysis = await self.gemini.generate_structured(
            prompt=prompt,
            response_schema=VisualGapReport
        )
        
        # 4. Add visual examples
        gap_analysis.examples = await self._generate_visual_examples(
            your_photos, 
            competitor_photos,
            gap_analysis
        )
        
        return gap_analysis
    
    async def _batch_analyze_images(
        self, 
        images: List[Image],
        analysis_type: str
    ) -> Dict:
        """
        Batch process images with Gemini Vision.
        """
        prompt = f"""
        Analyze these {analysis_type} images as a set.
        
        For each image, evaluate:
        1. Lighting quality (1-10): Natural vs studio, direction, softness
        2. Composition (1-10): Framing, rule of thirds, focal point
        3. Color saturation (1-10): Vibrant vs muted, consistency
        4. Professional score (1-10): Overall quality
        5. Dominant colors: List main colors
        6. Mood/vibe: Describe feeling (warm, cold, rustic, modern, etc.)
        
        Then provide aggregated insights:
        - Overall style/aesthetic
        - Consistency score (1-10)
        - Strengths (top 3)
        - Weaknesses (top 3)
        - Recommended improvements
        
        Return structured JSON.
        """
        
        # Gemini can handle multiple images in one call
        response = await self.gemini.generate_multimodal(
            prompt=prompt,
            images=images
        )
        
        return response
```

### **Context Loop (Temporal Intelligence)**
```python
# backend/app/services/intelligence/context_loop.py

class ContextLoop:
    """
    Tracks changes over time to detect trends and validate insights.
    """
    
    async def detect_price_trends(
        self,
        competitor_id: str,
        historical_menus: List[MenuSnapshot]
    ) -> PriceTrendAnalysis:
        """
        Analyze how competitor prices have changed over time.
        """
        if len(historical_menus) < 2:
            return PriceTrendAnalysis(
                status="INSUFFICIENT_DATA",
                message="Need at least 2 menu snapshots to detect trends"
            )
        
        # Sort by date
        menus = sorted(historical_menus, key=lambda m: m.date)
        
        # Compare prices for same items
        price_changes = []
        for item_name in menus[0].items.keys():
            if item_name in menus[-1].items:
                old_price = menus[0].items[item_name]
                new_price = menus[-1].items[item_name]
                change_pct = ((new_price - old_price) / old_price) * 100
                
                price_changes.append({
                    "item": item_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_pct": change_pct,
                    "time_span_days": (menus[-1].date - menus[0].date).days
                })
        
        # Gemini interprets the trend
        prompt = f"""
        Analyze these price changes for competitor {competitor_id}:
        
        {json.dumps(price_changes, indent=2)}
        
        Determine:
        1. Overall pricing strategy (raising, lowering, stable)
        2. Category-specific trends (e.g., protein prices up, sides down)
        3. Likely causes (inflation, competition, demand)
        4. Strategic implications for user
        5. Recommended response
        
        Return structured analysis.
        """
        
        analysis = await self.gemini.generate_structured(
            prompt=prompt,
            response_schema=PriceTrendAnalysis
        )
        
        return analysis
    
    async def cross_reference_data_sources(
        self,
        claim: str,
        sources: List[DataSource]
    ) -> VerificationResult:
        """
        Verify a claim against multiple data sources.
        """
        evidence = []
        for source in sources:
            relevant_data = source.search(claim)
            if relevant_data:
                evidence.append({
                    "source": source.name,
                    "data": relevant_data,
                    "date": source.last_updated,
                    "reliability": source.reliability_score
                })
        
        # Gemini evaluates contradictions
        prompt = f"""
        Verify this claim:
        "{claim}"
        
        Evidence from multiple sources:
        {json.dumps(evidence, indent=2)}
        
        Determine:
        1. Is the claim supported? (YES/NO/PARTIAL)
        2. Confidence (0-100%)
        3. Are there contradictions between sources?
        4. Which source is most reliable?
        5. Final verdict with reasoning
        
        Return structured verification.
        """
        
        verification = await self.gemini.generate_structured(
            prompt=prompt,
            response_schema=VerificationResult
        )
        
        return verification
```

---

## 📱 API Reference

### **Intelligence Endpoint (Main)**
```http
POST /api/v1/intelligence/analyze

Request Body:
{
  "location": "Calle 5 #23-45, Bogotá, Colombia",  // REQUIRED
  "menu_photo": "data:image/jpeg;base64,...",       // OPTIONAL
  "sales_csv": "base64_encoded_csv",                // OPTIONAL
  "social_handles": {                               // OPTIONAL
    "instagram": "@mi_restaurante",
    "facebook": "MiRestaurantePage"
  },
  "search_radius_meters": 500,                      // DEFAULT: 500
  "max_competitors": 5,                             // DEFAULT: 5
  "analysis_depth": "DEEP"                          // QUICK|STANDARD|DEEP|EXHAUSTIVE
}

Response (after 3-5 minutes):
{
  "session_id": "uuid",
  "status": "COMPLETED",
  "intelligence_report": {
    "executive_summary": "...",
    "neighborhood": { ... },
    "competitors": [ ... ],
    "visual_gaps": { ... },
    "price_positioning": { ... },
    "bcg_matrix": { ... },
    "campaigns": [ ... ],
    "gemini_insights": { ... }
  },
  "confidence_scores": { ... },
  "api_usage": {
    "gemini_tokens": 45230,
    "gemini_calls": 12,
    "cost_usd": 3.45
  }
}
```

### **WebSocket for Real-Time Progress**
```javascript
// Frontend connects to WebSocket for live updates
const ws = new WebSocket('ws://localhost:8000/ws/intelligence/${sessionId}');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  console.log(update);
  // {
  //   "step": "COMPETITOR_DISCOVERY",
  //   "progress": 35,
  //   "message": "Found 5 competitors, enriching data...",
  //   "eta_seconds": 180
  // }
};
```

---

## 🎓 Learn More

- **[Full Documentation](./docs/README.md)** - Complete technical guide
- **[Architecture Deep Dive](./docs/ARCHITECTURE.md)** - System design
- **[Gemini Integration](./docs/GEMINI_INTEGRATION.md)** - How we use Gemini 3
- **[API Reference](./docs/API.md)** - Complete endpoint documentation
- **[Contributing Guide](./CONTRIBUTING.md)** - Join development

---

## 🏆 Built for Gemini 3 Hackathon

RestaurantIQ showcases Gemini 3's most advanced capabilities:

| Capability | How We Use It | Impact |
|------------|---------------|--------|
| **Multimodal Vision** | Analyze menus, dishes, ambiance, social posts, customer photos | Core differentiator |
| **Long Context (1M tokens)** | Process all competitor data simultaneously | Enables holistic analysis |
| **Agentic Patterns** | Marathon Agent for autonomous data gathering | Industry-first feature |
| **Function Calling** | Dynamic tool use (search, scrape, geocode) | Enables Scout Agent |
| **Advanced Reasoning** | Strategic business insights from raw data | Turns data into decisions |
| **Self-Verification** | Cross-reference sources, assign confidence | Enterprise-grade reliability |

**What makes this a showcase:**
1. **Not a chatbot** - Autonomous intelligence platform
2. **Real multimodal** - Processes dozens of images per analysis
3. **Production-ready** - Handles edge cases, errors, rate limits
4. **Measurable impact** - Delivers actionable insights worth $5,000

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Priority areas:**
- Additional data sources (TripAdvisor, Uber Eats, etc.)
- More sophisticated ML models
- International market support
- White-label dashboard

---

## 📜 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

- **Google Gemini 3** - For making multimodal AI accessible and powerful
- **Gemini 3 Hackathon** - For the challenge that inspired this project
- **Early Testers** - Restaurant owners who provided feedback

---

## 📞 Contact & Support

- **Live Demo**: [restaurantiq.vercel.app](https://restaurantiq.vercel.app)
- **Documentation**: [docs.restaurantiq.app](https://docs.restaurantiq.app)
- **Issues**: [GitHub Issues](https://github.com/DuqueOM/RestaurantIQ/issues)
- **Email**: support@restaurantiq.app

---

**Built with ❤️ and 🤖 for the restaurant industry**

*RestaurantIQ - Competitive Intelligence, Powered by AI*