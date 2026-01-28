# Architecture - MenuPilot

## System Overview

MenuPilot implements advanced agentic patterns optimized for **Gemini 3**:

### Core Agentic Patterns
- **Marathon Agent**: Autonomous pipeline orchestration with **long-term memory** leveraging Gemini 3's 1M token context window
- **Vibe Engineering**: Self-verification loop with auto-correction and quality thresholds
- **Multi-level Thinking**: Configurable reasoning depth (Quick/Standard/Deep/Exhaustive)
- **Thought Signatures**: Full reasoning trace with plan, observations, assumptions, and verification checks

### Key Features (Hackathon Update)
- **Business Context Input**: Voice/text input for restaurant profiling
- **Professional BCG Matrix**: Uses gross profit, margin, and growth rate (not just revenue)
- **Multi-file Menu Upload**: Support for multiple PDFs and images
- **Agent Dashboard (War Room)**: Real-time visualization of agent workflow
- **Personalized Campaigns**: Specific, actionable recommendations with ready-to-use copy
- **Competitor Intelligence** (NEW): Real-time competitive analysis from URLs, images, social media
- **Sentiment Analysis** (NEW): Multi-modal customer sentiment from reviews + photos
- **Modular Gemini Agents** (NEW): Refactored architecture with specialized agents

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         MenuPilot Architecture                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐     ┌──────────────────────────────────────────────────┐ │
│  │   Frontend   │     │                Backend (FastAPI)                 │ │
│  │   (Next.js)  │───▶│                                                  │ │
│  │              │     │  ┌───────────────────────────────────────────┐   │ │
│  │  - Upload UI │     │  │         Analysis Orchestrator             │   │ │
│  │  - BCG Chart │     │  │         (Marathon Agent Pattern)          │   │ │
│  │  - Campaigns │     │  │  ┌─────────────────────────────────────┐  │   │ │
│  │  - Thought   │     │  │  │    Verification Agent               │  │   │ │
│  │    Signature │     │  │  │    (Vibe Engineering Pattern)       │  │   │ │
│  │  - Verify    │     │  │  │  - Self-verification loop           │  │   │ │
│  │    Results   │     │  │  │  - Auto-improvement                 │  │   │ │
│  └──────────────┘     │  │  │  - Quality threshold checks         │  │   │ │
│                       │  │  └─────────────────────────────────────┘  │   │ │
│                       │  │  ┌─────────────────────────────────────┐  │   │ │
│                       │  │  │        Gemini 3 Agents (Modular)    │  │   │ │
│                       │  │  │  - BaseAgent (retry, rate limit)    │  │   │ │
│                       │  │  │  - MultimodalAgent (vision+text)    │  │   │ │
│                       │  │  │  - ReasoningAgent (deep analysis)   │  │   │ │
│                       │  │  │  - VerificationAgent (self-check)   │  │   │ │
│                       │  │  │  - OrchestratorAgent (marathon)     │  │   │ │
│                       │  │  └─────────────────────────────────────┘  │   │ │
│                       │  │  ┌─────────────────────────────────────┐  │   │ │
│                       │  │  │      Intelligence Services          │  │   │ │
│                       │  │  │  - CompetitorIntelligence           │  │   │ │
│                       │  │  │  - SentimentAnalyzer                │  │   │ │
│                       │  │  └─────────────────────────────────────┘  │   │ │
│                       │  └───────────────────────────────────────────┘   │ │
│                       │                                                  │ │
│                       │  ┌───────────────────────────────────────────┐   │ │
│                       │  │              ML Services                  │   │ │
│                       │  │  ┌─────────────┐  ┌─────────────────────┐ │   │ │
│                       │  │  │   XGBoost   │  │  Neural Predictor   │ │   │ │
│                       │  │  │  Predictor  │  │  - LSTM             │ │   │ │
│                       │  │  │             │  │  - Transformer      │ │   │ │
│                       │  │  │             │  │  - MC Dropout       │ │   │ │
│                       │  │  │             │  │  - Uncertainty      │ │   │ │
│                       │  │  └─────────────┘  └─────────────────────┘ │   │ │
│                       │  │  ┌─────────────┐  ┌─────────────────────┐ │   │ │
│                       │  │  │    BCG      │  │    Campaign         │ │   │ │
│                       │  │  │  Classifier │  │    Generator        │ │   │ │
│                       │  │  └─────────────┘  └─────────────────────┘ │   │ │
│                       │  └───────────────────────────────────────────┘   │ │
│                       │                                                  │ │
│                       │  ┌─────────────────┐  ┌───────────────┐          │ │
│                       │  │  Gemini 3 API   │  │  Local Store  │          │ │
│                       │  │  (Google Cloud) │  │  (SQLite)     │          │ │
│                       │  └─────────────────┘  └───────────────┘          │ │
│                       └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 14)

**Stack:**
- Next.js 14 with App Router
- TypeScript
- TailwindCSS
- Recharts (visualizations)
- Lucide React (icons)

**Key Components:**
| Component | Purpose |
|-----------|---------|
| `FileUpload` | Reorganized upload: CSV → Menu (multiple) → Additional media |
| `BusinessContextInput` | Voice/text input for business profiling with quick suggestions |
| `AnalysisPanel` | Run BCG, predictions, campaigns with progress tracking |
| `BCGChart` | Interactive scatter plot with quadrant visualization |
| `BCGResultsPanel` | Top 4 category cards + collapsible product lists by BCG class |
| `CampaignCards` | Display personalized campaigns with full copy |
| `ThoughtSignature` | Fully expandable AI reasoning trace with thinking levels |
| `AgentDashboard` | "War Room" - Timeline, vibe monitor, thought trace modal |
| `CompetitorDashboard` | (NEW) Compare prices, find gaps, strategic recommendations |
| `SentimentDashboard` | (NEW) Customer sentiment from reviews + visual analysis |

### Backend (FastAPI)

**Stack:**
- FastAPI 0.109
- SQLAlchemy (async)
- Pydantic v2
- XGBoost
- Tesseract OCR

**API Endpoints:**

```
# Data Ingestion
POST /api/v1/ingest/menu       - Upload menu image
POST /api/v1/ingest/dishes     - Upload dish photos
POST /api/v1/ingest/sales      - Upload sales CSV

# Analysis
POST /api/v1/analyze/bcg       - Run BCG classification
POST /api/v1/predict/sales     - XGBoost predictions
POST /api/v1/predict/neural    - Neural network predictions with uncertainty
POST /api/v1/campaigns/generate - Create campaign proposals

# Agentic Endpoints
POST /api/v1/orchestrator/run  - Run complete autonomous pipeline
GET  /api/v1/orchestrator/status/{id} - Get orchestrator session status
POST /api/v1/verify/analysis   - Run verification agent
WS   /api/v1/ws/analysis/{id}  - WebSocket for real-time progress updates

# Intelligence Services (NEW - WOW Factors)
POST /api/v1/competitors/analyze    - Analyze competitor menus/pricing
POST /api/v1/sentiment/analyze      - Multi-modal sentiment analysis
GET  /api/v1/analysis/complete/{id} - Get full analysis with all insights
POST /api/v1/analysis/executive-summary - Generate executive summary

# Session & Models
GET  /api/v1/session/{id}      - Get session data
GET  /api/v1/session/{id}/export - Export results
GET  /api/v1/models/info       - Get ML model status
```

### Gemini Agent

**Agentic Workflow (Enhanced for Gemini 3):**

```
1. Marathon Agent Initialization
   └─▶ Load long-term context (1M token window)
   └─▶ Retrieve historical insights for this restaurant
   └─▶ Initialize thought signature

2. Business Context Processing
   └─▶ Voice/text input analysis
   └─▶ Restaurant profiling (cuisine, audience, location)
   └─▶ Competitive context extraction

3. Multi-Modal Menu Extraction
   └─▶ Multi-page PDF processing
   └─▶ OCR preprocessing with enhancement
   └─▶ Gemini Vision extraction
   └─▶ Structure validation & deduplication

4. Professional BCG Classification
   └─▶ Gross profit calculation (revenue - cost)
   └─▶ Margin and profitability index
   └─▶ Growth rate analysis
   └─▶ Quadrant-specific strategic recommendations

5. Sales Prediction (XGBoost + Neural Ensemble)
   └─▶ Feature engineering (temporal, promotional)
   └─▶ Multi-scenario forecasting
   └─▶ Confidence intervals with MC Dropout

6. Personalized Campaign Generation
   └─▶ BCG-based targeting (Stars, Question Marks, etc.)
   └─▶ Specific discount calculations with exact prices
   └─▶ Ready-to-use social media copy
   └─▶ Expected ROI estimation

7. Vibe Engineering Self-Verification
   └─▶ Consistency checks across all outputs
   └─▶ Auto-correction loop (max 3 iterations)
   └─▶ Quality threshold enforcement
   └─▶ Thought trace logging

8. Competitor Intelligence (NEW)
   └─▶ Multi-source data collection (URLs, images, social)
   └─▶ Price comparison analysis
   └─▶ Product gap identification
   └─▶ Strategic positioning recommendations

9. Sentiment Analysis (NEW)
   └─▶ Text review extraction and NLP
   └─▶ Customer photo visual analysis
   └─▶ Cross-reference with menu items
   └─▶ Item-level sentiment scoring
```

### Modular Gemini Agent Architecture (NEW)

```
backend/app/services/gemini/
├── __init__.py              # Module exports
├── base_agent.py            # Core: retry logic, rate limiting, token tracking
├── multimodal_agent.py      # Vision + text extraction capabilities
├── reasoning_agent.py       # Deep analysis & strategic thinking
├── verification_agent.py    # Self-verification loop (Vibe Engineering)
└── orchestrator_agent.py    # Marathon pattern coordinator

Key Features:
┌─────────────────────────────────────────────────────────────────────┐
│ GeminiBaseAgent                                                     │
│  - Exponential backoff retry (tenacity)                             │
│  - Rate limiting (requests/minute)                                  │
│  - Token usage tracking & cost estimation                           │
│  - Structured logging with correlation IDs                          │
│  - Response caching for cost optimization                           │
├─────────────────────────────────────────────────────────────────────┤
│ MultimodalAgent                                                     │
│  - Image + text combined analysis                                   │
│  - Multi-page PDF processing                                        │
│  - OCR preprocessing with enhancement                               │
│  - Structured JSON output parsing                                   │
├─────────────────────────────────────────────────────────────────────┤
│ ReasoningAgent                                                      │
│  - Multi-level thinking (Quick/Standard/Deep/Exhaustive)            │
│  - Thought signatures with confidence scores                        │
│  - Strategic analysis capabilities                                  │
│  - Cross-data reasoning                                             │
├─────────────────────────────────────────────────────────────────────┤
│ VerificationAgent                                                   │
│  - Self-verification loop (max 3 iterations)                        │
│  - Quality threshold enforcement (0.8 default)                      │
│  - Auto-correction with feedback                                    │
│  - Consistency checks across outputs                                │
├─────────────────────────────────────────────────────────────────────┤
│ OrchestratorAgent                                                   │
│  - Pipeline stage management                                        │
│  - Checkpoint save/restore for long-running tasks                   │
│  - WebSocket progress streaming                                     │
│  - Error recovery and partial results                               │
└─────────────────────────────────────────────────────────────────────┘
```

### ML Pipeline

```
Sales Data ─▶ Feature Engineering ─▶ XGBoost Training ─▶ Predictions
    │                │                                        │
    ├─ day_of_week   ├─ rolling_avg_7d                       ├─ baseline
    ├─ is_weekend    ├─ rolling_avg_30d                      ├─ promo scenario
    ├─ price         ├─ lag_1d                               └─ marketing scenario
    ├─ promo_flag    └─ lag_7d
    └─ image_score
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Input                                                     │
│     │                                                           │
│     ├─▶ Menu Image ─────▶ OCR + Gemini ─────▶ Menu Items JSON │
│     │                                                           │
│     ├─▶ Dish Photos ────▶ Gemini Vision ────▶ Image Scores    │
│     │                                                           │
│     └─▶ Sales CSV ──────▶ Pandas Parse ─────▶ Sales Records   │
│                                                                 │
│                              ▼                                  │
│                     ┌────────────────┐                          │
│                     │ Session Store  │                          │
│                     └───────┬────────┘                          │
│                             │                                   │
│                             ▼                                   │
│  Analysis                                                       │
│      │                                                          │
│      ├─▶ BCG Classification ─────▶ Product Profiles            │
│      │                                                          │
│      ├─▶ Sales Prediction ───────▶ 14-day Forecasts            │
│      │                                                          │
│      └─▶ Campaign Generation ────▶ 3 Campaign Proposals        │
│                                                                 │
│                              ▼                                  │
│                     ┌────────────────┐                          │
│                     │  JSON Export   │                          │
│                     └────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Option 3: Cloud Deployment

**Recommended platforms:**
- **Backend**: Google Cloud Run, Railway, Render
- **Frontend**: Vercel, Netlify

## Security Considerations

1. **API Key Protection**: Never commit GEMINI_API_KEY
2. **CORS**: Configure for production domains
3. **File Uploads**: Validate file types and sizes
4. **Rate Limiting**: Add for production deployment
5. **Authentication**: Add user auth for multi-tenant use
