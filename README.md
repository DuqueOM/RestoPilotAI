# 🍽️ MenuPilot

**AI-Powered Restaurant Menu Optimization**

[![Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-blue)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MenuPilot is a multimodal AI assistant that helps small and medium restaurants optimize their menu, pricing, and marketing campaigns using real data and automated reasoning powered by **Google Gemini 3**.

---

## 🎯 What it Does

### Core Features
1. **Menu Extraction**: Upload a menu image → Get structured product catalog (OCR + Gemini multimodal)
2. **Visual Analysis**: Upload dish photos → Get attractiveness scores and presentation feedback
3. **BCG Classification**: Automatic product categorization (Star, Cash Cow, Question Mark, Dog)
4. **Sales Prediction**: Dual ML approach - XGBoost + Neural Networks (LSTM/Transformer)
5. **Campaign Generation**: AI-generated marketing campaigns with copy, scheduling, and rationale

### 🆕 WOW Factor Features (Hackathon Special)
6. **🎯 Competitor Intelligence**: Extract competitor menus from images/URLs, price comparison analysis, strategic positioning insights
7. **💬 Multi-Modal Sentiment Analysis**: Combine text reviews + customer photos for item-level sentiment with portion perception
8. **🧠 Thought Signatures**: Multi-level transparent reasoning traces (QUICK/STANDARD/DEEP/EXHAUSTIVE)
9. **✅ Autonomous Verification**: Self-improving analysis with quality checks (Vibe Engineering pattern)
10. **🏃 Pipeline Orchestration**: Marathon Agent pattern with checkpoints for reliable long-running tasks
11. **📊 Executive Summary Generation**: AI-synthesized strategic recommendations from all data sources
12. **🔌 Real-time WebSocket Progress**: Live progress updates during analysis pipeline execution

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Recommended: Python 3.11 or 3.12 (for easiest installs)
- Node.js 18+
- Docker (optional)
- [Gemini API Key](https://aistudio.google.com/apikey)

Note: If you're using Python 3.13, some scientific packages may build from source depending on your platform. If install fails, use Python 3.11/3.12.

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/menupilot.git
cd menupilot

# Set your API key
export GEMINI_API_KEY=your_api_key_here

# Run with Docker Compose
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development (with Makefile - Recommended)

```bash
# Quick setup
make setup              # Creates venv, installs all dependencies

# Configure API key (interactive)
./scripts/setup_api_key.sh

# Run!
make run                # Starts backend (8000) and frontend (3000)
```

### Option 3: Local Development (manual)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal, from project root)
cd frontend
npm install
npm run dev
```

### Option 4: Using Conda (recommended for Python version control)

```bash
# Create environment with Python 3.11
conda create -n menupilot python=3.11 -y
conda activate menupilot

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 📊 How Gemini 3 is Used

MenuPilot leverages Gemini 3's capabilities extensively:

| Feature | Gemini 3 Capability |
|---------|---------------------|
| Menu extraction from images | **Multimodal vision** + text extraction |
| Dish photo analysis | **Visual understanding** for quality scoring |
| BCG strategic insights | **Reasoning** for business recommendations |
| Campaign copy generation | **Content generation** with context |
| Autonomous verification | **Agentic function calling** for quality checks |
| Thought signatures | **Multi-level transparent reasoning** traces |
| Pipeline orchestration | **Long-running task coordination** with checkpoints |

### Agentic Workflow Patterns

MenuPilot implements three key agentic patterns from the hackathon tracks:

**1. Marathon Agent Pattern** - Autonomous pipeline orchestration:
```python
orchestrator = AnalysisOrchestrator()
result = await orchestrator.run_full_pipeline(
    session_id=session_id,
    menu_images=[...],
    thinking_level=ThinkingLevel.DEEP,
    auto_verify=True,  # Self-verification loop
)
```

**2. Vibe Engineering Pattern** - Self-verification and improvement:
```python
verification = await verification_agent.verify_analysis(
    analysis_data,
    thinking_level=ThinkingLevel.EXHAUSTIVE,
    auto_improve=True,  # Iteratively improve until quality threshold
)
```

**3. Thought Signatures with Levels**:
- `QUICK` - Fast, surface-level analysis
- `STANDARD` - Normal analysis depth
- `DEEP` - Multi-perspective analysis
- `EXHAUSTIVE` - Maximum depth with multiple verification passes

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────────┐
│    Frontend     │     │           Backend (FastAPI)             │
│    (Next.js)    │───▶│                                         │
│                 │     │  ┌─────────────────────────────────┐    │
│  Upload UI      │     │  │     Analysis Orchestrator       │    │
│  BCG Chart      │     │  │     (Marathon Agent Pattern)    │    │
│  Campaigns      │     │  │  ┌───────────────────────────┐  │    │
│  Thought Sig    │     │  │  │    Gemini 3 Agent         │  │    │
│  Verification   │     │  │  │  - Menu Extraction        │  │    │
│                 │     │  │  │  - Visual Analysis        │  │    │
└─────────────────┘     │  │  │  - Campaign Generation    │  │    │
                        │  │  └───────────────────────────┘  │    │
                        │  │  ┌───────────────────────────┐  │    │
                        │  │  │  Verification Agent       │  │    │
                        │  │  │  (Vibe Engineering)       │  │    │
                        │  │  │  - Self-verification      │  │    │
                        │  │  │  - Auto-improvement       │  │    │
                        │  │  └───────────────────────────┘  │    │
                        │  └─────────────────────────────────┘    │
                        │  ┌─────────────────────────────────┐    │
                        │  │        ML Services              │    │
                        │  │  - BCG Classifier               │    │
                        │  │  - XGBoost Predictor            │    │
                        │  │  - Neural Predictor (LSTM/Trans)│    │
                        │  └─────────────────────────────────┘    │
                        └─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
menupilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              # REST API endpoints
│   │   │   └── websocket.py           # 🆕 WebSocket progress streaming
│   │   ├── core/
│   │   │   ├── logging_config.py      # 🆕 Structured logging
│   │   │   └── cache.py               # 🆕 Multi-tier caching system
│   │   ├── services/
│   │   │   ├── gemini/                # 🆕 Modular Gemini Agent Architecture
│   │   │   │   ├── base_agent.py      # Core infrastructure (retry, rate limit, cache)
│   │   │   │   ├── multimodal_agent.py # Vision + text extraction
│   │   │   │   ├── reasoning_agent.py  # Deep analysis & strategy
│   │   │   │   ├── verification_agent.py # Self-verification loop
│   │   │   │   └── orchestrator_agent.py # Marathon pattern coordinator
│   │   │   ├── competitor_intelligence.py # 🆕 Competitive analysis
│   │   │   ├── sentiment_analyzer.py   # 🆕 Multi-modal sentiment
│   │   │   ├── bcg_classifier.py      # BCG matrix classification
│   │   │   ├── sales_predictor.py     # XGBoost forecasting
│   │   │   ├── neural_predictor.py    # LSTM/Transformer deep learning
│   │   │   └── campaign_generator.py  # AI campaign generation
│   │   ├── models/
│   │   │   ├── analysis.py            # Core analysis models
│   │   │   ├── competitor.py          # 🆕 Competitor intelligence models
│   │   │   ├── sentiment_analysis.py  # 🆕 Sentiment models
│   │   │   └── thought_trace.py       # 🆕 AI reasoning trace models
│   │   └── schemas/                   # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx               # Main UI
│   │   └── components/
│   │       ├── CompetitorDashboard.tsx # 🆕 Competitive insights UI
│   │       └── SentimentDashboard.tsx  # 🆕 Sentiment analysis UI
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── DATA_CARD.md
│   ├── MODEL_CARD.md
│   ├── ARCHITECTURE.md
│   └── GEMINI_INTEGRATION.md          # 🆕 Detailed Gemini usage guide
├── docker-compose.yml
└── README.md
```

---

## 📋 API Reference

### Ingest Endpoints

```http
POST /api/v1/ingest/menu
Content-Type: multipart/form-data
file: <menu_image>
```

```http
POST /api/v1/ingest/sales
Content-Type: multipart/form-data
file: <sales.csv>
session_id: <session_id>
```

### Analysis Endpoints

```http
POST /api/v1/analyze/bcg?session_id=<id>
POST /api/v1/predict/sales?session_id=<id>&horizon_days=14
POST /api/v1/campaigns/generate?session_id=<id>&num_campaigns=3
```

Full API documentation: http://localhost:8000/docs

---

## 📄 Documentation

- [Data Card](docs/DATA_CARD.md) - Data processing and requirements
- [Model Card](docs/MODEL_CARD.md) - ML model details and limitations
- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Gemini Integration](docs/GEMINI_INTEGRATION.md) - 🆕 Detailed guide on Gemini 3 usage, agent architecture, and API patterns

---

## 📝 Submission Description (200 words)

**MenuPilot** is an autonomous multimodal AI assistant for restaurant optimization built with the Gemini 3 API. It implements three key agentic patterns: **Marathon Agent** for reliable long-running pipelines with checkpoints, **Vibe Engineering** for self-verification and iterative improvement, and **multi-level Thought Signatures** for transparent reasoning.

**Gemini 3 Integration:**
- **Multimodal extraction**: Menu images processed with Gemini vision + OCR hybrid approach
- **Visual analysis**: Dish photographs scored for presentation quality and appeal
- **Autonomous orchestration**: Complete analysis pipeline runs with checkpoints for reliability
- **Self-verification loop**: Analysis verified and auto-improved until quality thresholds met
- **Multi-level thinking**: Quick/Standard/Deep/Exhaustive reasoning depth options

**Key Features:**
- BCG Matrix classification with AI-enhanced strategic insights
- Dual ML prediction: XGBoost + Neural Networks (LSTM/Transformer) with uncertainty quantification
- AI-generated marketing campaigns aligned with product classification
- 95% confidence intervals on all predictions
- Transparent thought traces at every step

**Technical Stack:** FastAPI backend, Next.js frontend, PyTorch deep learning, Docker deployment

MenuPilot demonstrates how Gemini 3 can serve as an **autonomous intelligent orchestrator** for PYMEs, combining multimodal understanding, agentic coordination, self-verification, and sophisticated ML to deliver measurable, explainable business value.

---

## ⚡ Quick Commands Reference

```bash
# === SETUP ===
make setup                    # Full setup (backend + frontend)
make setup-backend            # Backend only
make setup-frontend           # Frontend only

# === RUN ===
make run                      # Run both (backend:8000, frontend:3000)
make run-backend              # Backend only
make run-frontend             # Frontend only

# === DOCKER ===
make docker                   # Build and run with Docker
docker-compose up --build     # Same as above

# === TESTING ===
make test                     # Run backend tests
make lint                     # Run linters

# === CONDA (alternative) ===
conda activate menupilot      # Activate environment
uvicorn app.main:app --reload --port 8000  # Run backend
```

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

- Built for the [Gemini 3 Hackathon](https://gemini3.devpost.com/)
- Powered by [Google Gemini 3 API](https://ai.google.dev/)
