# RestoPilotAI — Backend

> FastAPI backend powering multimodal AI restaurant intelligence with Google Gemini 3.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ with async/await |
| **AI Engine** | Google Gemini 3 (`google-genai` 1.0.0) |
| **ML/DL** | scikit-learn, XGBoost, PyTorch (LSTM/Transformer) |
| **Database** | SQLAlchemy 2.0 + SQLite (dev) / PostgreSQL (prod) |
| **Cache** | Redis 7 + in-memory LRU |
| **OCR/Vision** | Pillow, pytesseract, pdf2image, PyMuPDF |
| **Real-time** | WebSocket (native FastAPI) |
| **Logging** | Loguru + structlog |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Version: 1.0.0
│   ├── main.py                  # FastAPI app, lifespan, CORS, router registration
│   ├── api/
│   │   ├── deps.py              # Dependency injection (settings, DB sessions)
│   │   └── routes/
│   │       ├── analysis.py      # Analysis, prediction, chat endpoints
│   │       ├── business.py      # Ingestion, session, location, demo endpoints
│   │       ├── campaigns.py     # Campaign generation endpoints
│   │       ├── creative.py      # Creative Autopilot, menu transform, Instagram
│   │       ├── grounding.py     # Google Search grounding endpoints
│   │       ├── marathon.py      # Marathon Agent orchestration + WebSocket
│   │       ├── monitoring.py    # Gemini usage monitoring
│   │       ├── progress.py      # WebSocket progress streaming
│   │       ├── streaming.py     # Streaming analysis endpoints
│   │       ├── vibe.py          # Vibe Engineering status/cancel
│   │       ├── vibe_engineering.py  # Verify analysis/campaigns
│   │       └── video.py         # Video analysis endpoints
│   ├── core/
│   │   ├── config.py            # Pydantic Settings, GeminiModel enum, all config
│   │   ├── cache.py             # Multi-layer caching system
│   │   ├── gemini_cache.py      # Gemini-specific response caching
│   │   ├── logging_config.py    # Structured logging setup
│   │   ├── model_fallback.py    # Automatic model fallback chain
│   │   ├── rate_limiter.py      # Token-aware rate limiting
│   │   └── websocket_manager.py # WebSocket connection & thought broadcasting
│   ├── models/
│   │   ├── analysis.py          # AnalysisSession, ProductProfile, MarathonCheckpoint
│   │   ├── business.py          # MenuCategory, MenuItem, SalesRecord
│   │   ├── competitor.py        # Competitor, CompetitorMenu, PriceComparison
│   │   ├── context.py           # BusinessContext, AudioContext, VideoContext
│   │   └── database.py          # Base, init_db, AsyncSessionLocal
│   ├── schemas/
│   │   ├── analysis.py          # BCG, Prediction, Campaign, ThoughtSignature schemas
│   │   └── business.py          # Menu, Sales, Extraction schemas
│   └── services/
│       ├── orchestrator.py      # AnalysisOrchestrator — 17-stage pipeline
│       ├── analysis/
│       │   ├── bcg.py           # BCGClassifier — Star/CashCow/QuestionMark/Dog
│       │   ├── menu_analyzer.py # MenuExtractor — multimodal menu digitization
│       │   ├── menu_engineering.py  # Menu engineering calculations
│       │   ├── menu_optimizer.py    # AI-powered menu optimization
│       │   ├── neural_predictor.py  # NeuralPredictor — LSTM/Transformer forecasting
│       │   ├── sales_predictor.py   # SalesPredictor — XGBoost regression
│       │   ├── sentiment.py     # SentimentAnalyzer — review & photo analysis
│       │   ├── pricing.py       # CompetitorIntelligenceService — price gaps
│       │   ├── advanced_analytics.py # Hourly/daily/seasonal patterns
│       │   ├── data_capability.py   # Data quality assessment
│       │   ├── context_processor.py # Audio/text context processing
│       │   ├── period_calculator.py # Date range calculations
│       │   └── visual_quality.py    # Image quality scoring
│       ├── campaigns/
│       │   └── generator.py     # CampaignGenerator — AI campaign proposals
│       ├── gemini/
│       │   ├── base_agent.py    # GeminiAgent — core with retry, rate limiting
│       │   ├── enhanced_agent.py    # EnhancedGeminiAgent — streaming, grounding, caching
│       │   ├── reasoning_agent.py   # ReasoningAgent — deep chain-of-thought
│       │   ├── multimodal.py    # MultimodalAgent — vision + audio + video
│       │   ├── advanced_multimodal.py # Advanced video/audio processing
│       │   ├── advanced_reasoning.py  # Multi-agent debate reasoning
│       │   ├── creative_autopilot.py  # CreativeAutopilotAgent — visual campaigns
│       │   ├── grounded_intelligence.py # Google Search grounding
│       │   ├── marathon_agent.py    # Marathon long-running task agent
│       │   ├── streaming_agent.py   # Streaming generation agent
│       │   ├── streaming_reasoning.py # Streaming + reasoning combined
│       │   ├── validation_agent.py  # Output validation agent
│       │   ├── verification.py  # VerificationAgent — self-verification loop
│       │   └── vibe_engineering.py   # VibeEngineeringAgent — quality assurance
│       ├── imagen/
│       │   └── campaign_generator.py # CampaignImageGenerator — native Gemini image gen
│       └── intelligence/
│           ├── competitor_finder.py  # ScoutAgent — competitor discovery
│           ├── competitor_parser.py  # Parse competitor input text
│           ├── data_enrichment.py    # CompetitorEnrichmentService — Google Maps
│           ├── geocoding.py     # Geocoding utilities
│           ├── location.py      # LocationService — place search
│           ├── neighborhood.py  # NeighborhoodAnalyzer — area analysis
│           ├── social_aesthetics.py  # Social media visual analysis
│           └── social_scraper.py     # Instagram/Facebook scraping
├── data/                        # Runtime data (uploads, outputs, models, DB)
├── tests/                       # pytest test suite
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Production container
└── pytest.ini                   # Test configuration
```

---

## API Endpoints Reference

All endpoints are prefixed with `/api/v1/`.

### Data Ingestion (`business.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingest/menu` | Upload menu images/PDFs for AI extraction |
| `POST` | `/ingest/sales` | Upload CSV/XLSX sales data |
| `POST` | `/ingest/dishes` | Upload dish photos for visual analysis |
| `POST` | `/ingest/audio` | Upload voice recordings for context |
| `POST` | `/business/setup-wizard` | Complete setup with all data types |

### Session Management (`business.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/session/{session_id}` | Get full session data with all analyses |
| `GET` | `/session/{session_id}/export` | Export session as JSON |
| `GET` | `/demo/load` | Load pre-built demo session |
| `GET` | `/demo/session` | Get demo session metadata |

### Location & Places (`business.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/location/search` | Search for places (Google Places API) |
| `POST` | `/location/identify-business` | Identify business from coordinates |
| `POST` | `/location/nearby-restaurants` | Find nearby competitor restaurants |
| `POST` | `/location/set-business` | Set business location for session |
| `POST` | `/location/enrich-competitor` | Enrich competitor with Google Maps data |

### Analysis (`analysis.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analysis/start` | Start analysis pipeline |
| `POST` | `/analyze/bcg` | Run BCG matrix classification |
| `POST` | `/analyze/competitors` | Run competitive analysis |
| `POST` | `/analyze/sentiment` | Run sentiment analysis |
| `POST` | `/analyze/advanced` | Run advanced analytics (patterns, trends) |
| `POST` | `/analyze/menu-optimization` | AI menu optimization recommendations |
| `POST` | `/analyze/capabilities` | Assess data quality and capabilities |
| `POST` | `/verify/analysis` | Verify analysis accuracy |
| `POST` | `/chat` | Conversational AI chat with session context |

### Predictions (`analysis.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/sales` | XGBoost sales prediction |
| `POST` | `/predict/neural` | Neural network (LSTM/Transformer) forecast |

### Campaigns (`campaigns.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/campaigns/generate` | Generate full campaign suite |
| `POST` | `/campaigns/quick-campaign` | Quick single campaign generation |
| `POST` | `/campaigns/refine-copy` | Refine campaign copywriting |
| `POST` | `/campaigns/regenerate-images` | Regenerate campaign images |

### Creative Studio (`creative.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/campaigns/creative-autopilot` | Full visual campaign pipeline |
| `POST` | `/creative/menu-transform` | AI menu style transformation (upload) |
| `POST` | `/creative/menu-transform-from-session` | Menu transform from session data |
| `POST` | `/creative/instagram-prediction` | Predict Instagram engagement |
| `GET` | `/session/{session_id}/files` | Get generated creative files |

### Grounding — Google Search (`grounding.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/grounding/verify` | Verify claims with Google Search |
| `POST` | `/grounding/competitor/analyze` | Grounded competitor analysis |
| `POST` | `/grounding/competitor/batch` | Batch competitor analysis |
| `POST` | `/grounding/trends/research` | Food industry trend research |
| `POST` | `/grounding/pricing/benchmarks` | Market pricing benchmarks |

### Marathon Agent (`marathon.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/marathon/start` | Start long-running analysis task |
| `GET` | `/marathon/status/{task_id}` | Get task status and progress |
| `GET` | `/marathon/stream/{task_id}` | Stream task events (SSE) |
| `GET` | `/marathon/thoughts/{task_id}` | Get AI thought traces |
| `POST` | `/marathon/cancel/{task_id}` | Cancel running task |
| `POST` | `/marathon/recover/{task_id}` | Recover from checkpoint |
| `POST` | `/marathon/debate` | Trigger multi-agent debate |
| `GET` | `/marathon/debates/{session_id}` | Get debate history |
| `POST` | `/marathon/debates/bcg/{session_id}` | BCG-specific debate |
| `WS` | `/ws/marathon/{task_id}` | WebSocket for real-time task events |

### Vibe Engineering (`vibe.py` + `vibe_engineering.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/vibe-engineering/status` | Get Vibe Engineering system status |
| `POST` | `/vibe-engineering/cancel` | Cancel running verification |
| `POST` | `/vibe-engineering/verify` | Quick verification check |
| `POST` | `/vibe-engineering/verify-analysis` | Deep analysis verification |
| `POST` | `/vibe-engineering/verify-campaign-assets` | Verify campaign quality |

### Video Analysis (`video.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/video/analyze` | Full video analysis (restaurant, kitchen, service) |
| `POST` | `/video/quick-check` | Quick video quality check |

### Streaming (`streaming.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/streaming/analysis/bcg` | Stream BCG analysis in real-time |

### Real-time WebSocket (`progress.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `WS` | `/ws/analysis/{session_id}` | Analysis progress events |
| `WS` | `/ws/live/{session_id}` | Live session updates |
| `GET` | `/ws/connections` | Active WebSocket connections |

### Monitoring (`monitoring.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/gemini/models` | List available Gemini models |
| `GET` | `/gemini/usage` | Token usage and cost stats |
| `POST` | `/gemini/reset-daily-stats` | Reset daily usage counters |

---

## Analysis Pipeline (Orchestrator)

The `AnalysisOrchestrator` runs a **17-stage autonomous pipeline**:

```
1.  INITIALIZED           → Setup session state
2.  DATA_INGESTION         → Process uploaded files
3.  MENU_EXTRACTION        → OCR + Gemini multimodal menu digitization
4.  COMPETITOR_PARSING     → Parse user-provided competitor info
5.  COMPETITOR_DISCOVERY   → ScoutAgent finds nearby competitors
6.  COMPETITOR_ENRICHMENT  → Google Maps Place Details enrichment
7.  COMPETITOR_VERIFICATION → Verify competitor data accuracy
8.  NEIGHBORHOOD_ANALYSIS  → Analyze area demographics & trends
9.  COMPETITOR_ANALYSIS    → Deep competitive intelligence
10. SENTIMENT_ANALYSIS     → Review & photo sentiment analysis
11. IMAGE_ANALYSIS         → Dish photo visual quality scoring
12. VISUAL_GAP_ANALYSIS    → Compare visual quality vs competitors
13. CONTEXT_PROCESSING     → Process audio/text business context
14. SALES_PROCESSING       → Parse and validate sales data
15. BCG_CLASSIFICATION     → BCG matrix classification
16. SALES_PREDICTION       → ML sales forecasting
17. CAMPAIGN_GENERATION    → AI marketing campaign proposals
18. STRATEGIC_VERIFICATION → Vibe Engineering quality check
19. VERIFICATION           → Final self-verification pass
20. COMPLETED              → All analyses finalized
```

Each stage supports **checkpoints** for crash recovery and produces **thought signatures** for transparent reasoning.

---

## Core Services

### Gemini Agent Hierarchy

```
GeminiBaseAgent (base_agent.py)
  ├── Rate limiting, retry logic, token tracking
  ├── Model fallback chain (PRO → FLASH → FLASH_2)
  └── Cost tracking

EnhancedGeminiAgent (enhanced_agent.py)
  ├── Google Search grounding integration
  ├── Streaming generation
  ├── Pydantic structured output validation
  └── Intelligent response caching

ReasoningAgent (reasoning_agent.py)
  ├── Chain-of-thought prompting
  ├── ThoughtTrace objects with confidence scores
  └── Multi-step reasoning chains

MultimodalAgent (multimodal.py)
  ├── Image analysis (menu OCR, dish quality)
  ├── Audio transcription & context extraction
  └── Video analysis (restaurant environment)

CreativeAutopilotAgent (creative_autopilot.py)
  ├── Campaign strategy generation
  ├── Creative concept development
  ├── Native Gemini image generation (gemini-3-pro-image-preview)
  ├── A/B variant generation
  └── Localized versions

GroundedIntelligenceService (grounded_intelligence.py)
  ├── Competitor research with auto-citations
  ├── Market trend analysis
  ├── Pricing benchmark research
  └── Source verification
```

### ML Models

| Model | Service | Purpose |
|-------|---------|---------|
| **XGBoost** | `SalesPredictor` | Time-series sales forecasting with features |
| **LSTM** | `NeuralPredictor` | Deep learning sequence prediction |
| **Transformer** | `NeuralPredictor` | Attention-based demand forecasting |
| **BCG Classifier** | `BCGClassifier` | Menu item strategic classification |

---

## Configuration

All configuration is via environment variables (see `.env.example`):

```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional (enables location features)
GOOGLE_MAPS_API_KEY=your_key_here

# Gemini Model Selection (defaults to PRO for max quality)
GEMINI_MODEL_PRIMARY=gemini-3-pro-preview
GEMINI_MODEL_REASONING=gemini-3-pro-preview
GEMINI_MODEL_VISION=gemini-3-pro-preview
GEMINI_MODEL_IMAGE_GEN=gemini-3-pro-image-preview
```

---

## Running

```bash
# Development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Docker
docker-compose up backend

# Tests
pytest tests/ -v
```

API documentation available at `http://localhost:8000/docs` (Swagger) and `http://localhost:8000/redoc` (ReDoc).
