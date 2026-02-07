# ⚡ RestoPilotAI — Quick Start Guide

> AI-Powered Competitive Intelligence Platform for Restaurants  
> Built with Google Gemini 3 Multimodal AI for the [Gemini 3 Hackathon](https://gemini3.devpost.com/)

---

## 🚀 Get Running in 5 Minutes

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Google Gemini API Key** — [Get one at AI Studio](https://aistudio.google.com/apikey)
- **Google Maps API Key** *(optional)* — for competitor discovery & location features

### Option 1: Quick Start (Local)

```bash
# 1. Clone the repository
git clone https://github.com/DuqueOM/RestoPilotAI.git
cd RestoPilotAI

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 4. Setup frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** — click **"Try Demo"** to see the full analysis pipeline.

### Option 2: Docker Compose

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

docker-compose up --build
```

Services: Backend (:8000), Frontend (:3000), PostgreSQL (:5432), Redis (:6379)

### Option 3: Cloud Run Deployment

```bash
# Prerequisites: gcloud CLI, Cloud Build + Cloud Run + Artifact Registry + Secret Manager APIs enabled

# Store secrets
echo -n "YOUR_GEMINI_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "YOUR_MAPS_KEY" | gcloud secrets create GOOGLE_MAPS_API_KEY --data-file=-

# Create Artifact Registry repo
gcloud artifacts repositories create restopilotai --repository-format=docker --location=us-central1

# Deploy both services
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1
```

---

## 🧪 Verify Everything Works

```bash
# 1. Backend health
curl http://localhost:8000/api/v1/health

# 2. Load demo data
curl -X POST http://localhost:8000/api/v1/demo/load

# 3. Check demo session
curl http://localhost:8000/api/v1/session/margarita-pinta-demo-001

# 4. Test WebSocket
wscat -c ws://localhost:8000/api/v1/marathon/ws/test

# 5. Frontend build
cd frontend && npm run build
```

---

## 📋 Analysis Pipeline (14 Stages)

RestoPilotAI runs a **Marathon Agent** — a 14-stage autonomous pipeline with checkpoints and state recovery:

```
Data Ingestion → Menu Extraction → Competitor Parsing → Competitor Discovery
→ Competitor Enrichment → Competitor Verification → Neighborhood Analysis
→ Competitor Analysis → Sentiment Analysis → Image Analysis → Visual Gap Analysis
→ Context Processing → Sales Processing → BCG Classification → Sales Prediction
→ Campaign Generation → Strategic Verification → ✅ Completed
```

Each stage produces **thought signatures** with plan, observations, reasoning, and assumptions.

---

## 🧠 Gemini 3 Capabilities Used

| Capability | Model | Where Used |
|------------|-------|------------|
| **Gemini 3 Pro** | `gemini-3-pro-preview` | All reasoning, analysis, classification |
| **Vision Analysis** | `gemini-3-pro-preview` | Menu photo extraction, dish analysis |
| **Native Video** | `gemini-3-pro-preview` | Restaurant walkthrough analysis |
| **Voice Understanding** | `gemini-3-pro-preview` | Audio transcription, business context |
| **Imagen 3** | `gemini-3-pro-image-preview` | Campaign visual generation |
| **Search Grounding** | Google Search | Competitor discovery, pricing benchmarks |
| **Deep Thinking** | ThinkingLevel (4 levels) | Cost-optimized reasoning depth |
| **Context Caching** | Gemini Cache API | Token reuse across pipeline stages |

### Agent Patterns

- **Marathon Agent** — 14-stage autonomous pipeline with checkpoints
- **Vibe Engineering** — Self-improving quality assurance loop
- **Multi-Agent Debate** — Adversarial reasoning for better decisions
- **Creative Autopilot** — End-to-end visual campaign generation

---

## 🗂️ Frontend Tabs

| Tab | Description | Gemini Capabilities |
|-----|-------------|---------------------|
| **Overview** | Dashboard with pipeline status and KPIs | Marathon Agent, all capabilities |
| **BCG Matrix** | Menu engineering & strategic classification | Pro, Thinking, Grounding, Vibe, Debate |
| **Competitors** | Real-time competitive intelligence | Pro, Grounding, Thinking, Debate |
| **Sentiment** | Multi-source NLP (Google Maps, Instagram, Facebook) | Pro, Grounding, Vibe, Debate |
| **AI Intelligence** | Interactive multimodal showcase (Video, Audio) | All capabilities |
| **Campaigns** | AI-generated marketing & Imagen 3 creative assets | Pro, Imagen 3, Creative Autopilot, Debate |

---

## ⚡ Quick Verification Commands

```bash
# Full pipeline test
curl -X POST "http://localhost:8000/api/v1/marathon/start?session_id=margarita-pinta-demo-001"

# BCG Analysis
curl -X POST "http://localhost:8000/api/v1/analyze/bcg?session_id=margarita-pinta-demo-001"

# Competitor Analysis
curl -X POST "http://localhost:8000/api/v1/analyze/competitors?session_id=margarita-pinta-demo-001"

# Sentiment Analysis
curl -X POST "http://localhost:8000/api/v1/analyze/sentiment?session_id=margarita-pinta-demo-001"

# Campaign Generation
curl -X POST "http://localhost:8000/api/v1/campaigns/generate?session_id=margarita-pinta-demo-001"

# Vibe Engineering Verification
curl -X POST http://localhost:8000/api/v1/vibe-engineering/verify-analysis \
  -H "Content-Type: application/json" \
  -d '{"analysis_type":"bcg","analysis_result":{},"source_data":{},"auto_improve":true}'

# Multi-Agent Debate
curl -X POST http://localhost:8000/api/v1/marathon/debate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Pricing strategy","context":"Restaurant analysis"}'
```

---

## 🚨 Troubleshooting

**Import errors:**
```bash
pip install google-genai --upgrade
```

**Frontend build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Gemini API errors:**
```bash
# Verify API key
echo $GEMINI_API_KEY
# Check quota at https://aistudio.google.com/apikey
```

**WebSocket not connecting:**
```bash
# Check if backend is running
lsof -i :8000
```

---

## ✅ Pre-Submission Checklist

```markdown
BACKEND:
- [x] 14-stage Marathon Agent pipeline
- [x] Creative Autopilot (Imagen 3)
- [x] Vibe Engineering QA loop
- [x] Multi-Agent Debate
- [x] Google Search Grounding
- [x] WebSocket streaming
- [x] Context Caching
- [x] No hardcoded secrets

FRONTEND:
- [x] 6 analysis tabs with Gemini capability badges
- [x] AI Intelligence tab with interactive Video + Audio
- [x] Real-time thought stream visualization
- [x] Build compiles without errors

DEPLOYMENT:
- [x] Docker + Docker Compose
- [x] Cloud Run (cloudbuild.yaml)
- [x] Public access (--allow-unauthenticated)

DOCUMENTATION:
- [x] README with architecture diagram
- [x] Backend README
- [x] Frontend README
- [x] Quick Start guide
```

---

**Last updated:** February 7, 2026  
**Hackathon:** [Gemini 3 Hackathon](https://gemini3.devpost.com/)  
**Deadline:** February 9, 2026 @ 5:00 PM PST
