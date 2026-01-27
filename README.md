# 🍽️ MenuPilot

**AI-Powered Restaurant Menu Optimization**

[![Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-blue)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MenuPilot is a multimodal AI assistant that helps small and medium restaurants optimize their menu, pricing, and marketing campaigns using real data and automated reasoning powered by **Google Gemini 3**.

---

## 🎯 What it Does

1. **Menu Extraction**: Upload a menu image → Get structured product catalog (OCR + Gemini multimodal)
2. **Visual Analysis**: Upload dish photos → Get attractiveness scores and presentation feedback
3. **BCG Classification**: Automatic product categorization (Star, Cash Cow, Question Mark, Dog)
4. **Sales Prediction**: ML-based forecasting for campaign scenarios (XGBoost)
5. **Campaign Generation**: AI-generated marketing campaigns with copy, scheduling, and rationale
6. **Thought Signatures**: Transparent reasoning traces for verifiable AI decisions

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- [Gemini API Key](https://aistudio.google.com/apikey)

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

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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
| Self-verification | **Agentic function calling** for quality checks |
| Thought signatures | **Transparent reasoning** traces |

### Agentic Workflow

```python
# MenuPilot uses Gemini function calling for orchestration
tools = [
    extract_menu,        # OCR + structure extraction
    analyze_dish_image,  # Visual appeal scoring
    classify_bcg,        # BCG matrix classification
    generate_campaign,   # Marketing campaign creation
    verify_analysis,     # Self-verification step
]
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────────────────┐
│    Frontend     │     │         Backend (FastAPI)       │
│    (Next.js)    │────▶│                                 │
│                 │     │  ┌─────────────────────────┐   │
│  Upload UI      │     │  │     Gemini 3 Agent      │   │
│  BCG Chart      │     │  │  - Menu Extraction      │   │
│  Campaigns      │     │  │  - Visual Analysis      │   │
│  Thought Sig    │     │  │  - Campaign Generation  │   │
│                 │     │  │  - Self-Verification    │   │
└─────────────────┘     │  └───────────┬─────────────┘   │
                        │              │                  │
                        │  ┌───────────▼─────────────┐   │
                        │  │    ML Services          │   │
                        │  │  - BCG Classifier       │   │
                        │  │  - Sales Predictor      │   │
                        │  │    (XGBoost)            │   │
                        │  └─────────────────────────┘   │
                        └─────────────────────────────────┘
```

---

## 📁 Project Structure

```
menupilot/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # API endpoints
│   │   ├── services/
│   │   │   ├── gemini_agent.py    # Gemini 3 orchestrator
│   │   │   ├── menu_extractor.py  # OCR + multimodal
│   │   │   ├── bcg_classifier.py  # BCG matrix logic
│   │   │   ├── sales_predictor.py # XGBoost forecasting
│   │   │   └── campaign_generator.py
│   │   ├── models/                # SQLAlchemy models
│   │   └── schemas/               # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx           # Main UI
│   │   └── components/
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── DATA_CARD.md
│   ├── MODEL_CARD.md
│   └── ARCHITECTURE.md
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

---

## 📝 Submission Description (200 words)

**MenuPilot** is a multimodal AI assistant for restaurant optimization built with the Gemini 3 API. It transforms scattered business data—menu images, dish photos, and sales records—into actionable insights and marketing strategies.

**Gemini 3 Integration:**
- **Multimodal extraction**: Menu images are processed using Gemini's vision capabilities combined with local OCR for robust text extraction
- **Visual analysis**: Dish photographs are scored for attractiveness using Gemini's visual understanding
- **Function calling**: An agentic workflow orchestrates BCG classification, campaign generation, and self-verification through structured tool calls
- **Thought signatures**: Every analysis includes a transparent reasoning trace showing the AI's plan, observations, and assumptions

**Key Features:**
- BCG Matrix classification (Star/Cash Cow/Question Mark/Dog)
- XGBoost-powered sales predictions for campaign scenarios
- AI-generated marketing campaigns with copy, scheduling, and rationale
- Self-verification loop that checks and corrects analysis quality

**Technical Stack:** FastAPI backend, Next.js frontend, Docker deployment

MenuPilot demonstrates how Gemini 3 can serve as an intelligent orchestrator for PYMEs, combining multimodal understanding, reasoning, and content generation to deliver measurable business value.

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

- Built for the [Gemini 3 Hackathon](https://gemini3.devpost.com/)
- Powered by [Google Gemini 3 API](https://ai.google.dev/)
