# Architecture - MenuPilot

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MenuPilot Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────────────────────────────────┐ │
│  │   Frontend   │     │              Backend (FastAPI)            │ │
│  │   (Next.js)  │────▶│                                          │ │
│  │              │     │  ┌─────────────────────────────────────┐ │ │
│  │  - Upload UI │     │  │         API Routes (/api/v1)        │ │ │
│  │  - BCG Chart │     │  │  /ingest  /analyze  /predict  /camp │ │ │
│  │  - Campaigns │     │  └─────────────┬───────────────────────┘ │ │
│  │  - Thought   │     │                │                         │ │
│  │    Signature │     │  ┌─────────────▼───────────────────────┐ │ │
│  └──────────────┘     │  │           Services Layer            │ │ │
│                       │  │                                      │ │ │
│                       │  │  ┌────────────┐  ┌────────────────┐ │ │ │
│                       │  │  │  Gemini    │  │  ML Services   │ │ │ │
│                       │  │  │  Agent     │  │  - BCG         │ │ │ │
│                       │  │  │            │  │  - Predictor   │ │ │ │
│                       │  │  │  - Extract │  │  - Campaign    │ │ │ │
│                       │  │  │  - Analyze │  │                │ │ │ │
│                       │  │  │  - Verify  │  └────────────────┘ │ │ │
│                       │  │  └─────┬──────┘                     │ │ │
│                       │  └────────┼────────────────────────────┘ │ │
│                       │           │                              │ │
│                       │           ▼                              │ │
│                       │  ┌─────────────────┐  ┌───────────────┐ │ │
│                       │  │  Gemini 3 API   │  │  Local Store  │ │ │
│                       │  │  (Google Cloud) │  │  (SQLite)     │ │ │
│                       │  └─────────────────┘  └───────────────┘ │ │
│                       └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
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
| `FileUpload` | Multi-dropzone for menu, dishes, sales |
| `AnalysisPanel` | Run BCG, predictions, campaigns |
| `BCGChart` | Interactive scatter plot visualization |
| `CampaignCards` | Display generated campaign proposals |
| `ThoughtSignature` | Show AI reasoning trace |

### Backend (FastAPI)

**Stack:**
- FastAPI 0.109
- SQLAlchemy (async)
- Pydantic v2
- XGBoost
- Tesseract OCR

**API Endpoints:**

```
POST /api/v1/ingest/menu       - Upload menu image
POST /api/v1/ingest/dishes     - Upload dish photos
POST /api/v1/ingest/sales      - Upload sales CSV

POST /api/v1/analyze/bcg       - Run BCG classification
POST /api/v1/predict/sales     - Generate predictions
POST /api/v1/campaigns/generate - Create campaign proposals

GET  /api/v1/session/{id}      - Get session data
GET  /api/v1/session/{id}/export - Export results
```

### Gemini Agent

**Agentic Workflow:**

```
1. Thought Signature Generation
   └─▶ Plan steps before execution

2. Menu Extraction
   └─▶ OCR preprocessing
   └─▶ Gemini multimodal extraction
   └─▶ Structure validation

3. Image Analysis
   └─▶ Visual attractiveness scoring
   └─▶ Presentation quality assessment

4. BCG Classification
   └─▶ Metric calculation
   └─▶ Rule-based classification
   └─▶ AI-enhanced insights

5. Campaign Generation
   └─▶ Strategy determination
   └─▶ Copy generation
   └─▶ Scheduling creation

6. Self-Verification
   └─▶ Consistency checks
   └─▶ Correction loop
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
│                        Data Flow                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Input                                                      │
│      │                                                           │
│      ├─▶ Menu Image ─────▶ OCR + Gemini ─────▶ Menu Items JSON  │
│      │                                                           │
│      ├─▶ Dish Photos ────▶ Gemini Vision ────▶ Image Scores     │
│      │                                                           │
│      └─▶ Sales CSV ──────▶ Pandas Parse ─────▶ Sales Records    │
│                                                                  │
│                              ▼                                   │
│                     ┌────────────────┐                          │
│                     │ Session Store  │                          │
│                     └───────┬────────┘                          │
│                             │                                    │
│                             ▼                                    │
│  Analysis                                                        │
│      │                                                           │
│      ├─▶ BCG Classification ─────▶ Product Profiles             │
│      │                                                           │
│      ├─▶ Sales Prediction ───────▶ 14-day Forecasts             │
│      │                                                           │
│      └─▶ Campaign Generation ────▶ 3 Campaign Proposals         │
│                                                                  │
│                              ▼                                   │
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
