# 🍽️ MenuPilot - AI-Powered Restaurant Menu Intelligence

<div align="center">

![MenuPilot](https://img.shields.io/badge/MenuPilot-Gemini%203%20Hackathon-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**Transform your restaurant's menu into a profit-maximizing machine with AI**

[Demo Video](#demo) • [Features](#-gemini-3-hackathon-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture)

</div>

---

## 🎯 The Problem

**70% of restaurants fail within their first 3 years.** The #1 reason? Poor menu decisions based on intuition rather than data.

Restaurant owners struggle with:
- 📊 No data-driven insights on which dishes to promote or remove
- 🎨 Expensive marketing campaigns that don't resonate
- 🔍 Zero visibility into competitor pricing and offerings
- ⏱️ Hours spent manually analyzing sales data

## 💡 The Solution

**MenuPilot** uses **Gemini 3** to transform raw menu images and sales data into actionable intelligence:

1. **Upload your menu** (image/PDF) → AI extracts all items automatically
2. **Connect sales data** (CSV) → BCG Matrix analysis identifies Stars, Dogs, and opportunities
3. **Generate campaigns** → Professional marketing assets in seconds
4. **Monitor competitors** → Real-time competitive intelligence with Google Search

---

## 🌟 Gemini 3 Hackathon Features

### 🎨 Creative Autopilot (Nano Banana Pro)

Generate professional marketing campaigns in seconds using `gemini-3-pro-image-preview`:

- **4K visual assets** with legible text in any language
- **Multi-language localization** - translates text INSIDE images
- **A/B testing variants** for campaign optimization
- **Brand consistency** using multi-reference image understanding

```bash
POST /api/v1/campaigns/creative-autopilot
# Generates: Instagram post, Story, Web banner, Printable flyer
```

**Why Gemini 3?** It's the ONLY model that generates accurate, legible text in images.

---

### ☯️ Vibe Engineering - Autonomous Quality Assurance

MenuPilot verifies its own work using `gemini-3-flash-preview`:

- **Self-evaluates** analysis quality across 4 dimensions
- **Automatically improves** until reaching 85% quality threshold
- **Zero human supervision** needed
- **Transparent metrics** showing improvement iterations

```bash
POST /api/v1/vibe-engineering/verify
# Returns: quality_score, improvements_made, iterations_count
```

---

### 🏃 Marathon Agent - Hours-Long Tasks

Run complex analyses without breaking:

- **Automatic checkpoints** every 60 seconds (Redis-backed)
- **Failure recovery** from last checkpoint
- **Real-time progress** via WebSocket
- **Graceful cancellation** support

```bash
POST /api/v1/marathon/start
WS   /api/v1/ws/marathon/{task_id}
```

---

### 🔍 Google Search Grounding

Every competitive analysis uses live data:

- **Current competitor prices** (not stale training data)
- **Recent reviews** from the last 30 days
- **Cited sources** for every claim made
- **Confidence scores** for each insight

```python
# Example grounded response
{
  "competitor_analysis": {...},
  "grounding_sources": [
    {"uri": "https://...", "title": "Competitor Menu Page"},
    {"uri": "https://...", "title": "Recent Yelp Review"}
  ]
}
```

---

### 🧠 Thought Signatures - Transparent AI Reasoning

See exactly how MenuPilot thinks:

| Level | Tokens | Use Case |
|-------|--------|----------|
| QUICK | ~500 | Simple queries |
| STANDARD | ~2000 | Regular analysis |
| DEEP | ~5000 | Strategic decisions |
| EXHAUSTIVE | ~10000 | Full competitive audits |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, for Marathon Agent checkpoints)
- Gemini API Key

### 1. Clone & Setup

```bash
git clone https://github.com/DuqueOM/MenuPilot.git
cd MenuPilot

# Backend
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### 2. Open Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Docker (Alternative)

```bash
docker-compose up --build
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────┐
│   Next.js 14    │────▶│          FastAPI Backend            │
│   Frontend      │     │                                     │
│                 │◀────│  ┌─────────────────────────────┐    │
│  • Dashboard    │     │  │     Gemini 3 Agents         │    │
│  • BCG Matrix   │     │  │                             │    │
│  • Campaigns    │     │  │  • ReasoningAgent           │    │
│  • Marathon     │     │  │  • CreativeAutopilotAgent   │    │
│    Monitor      │     │  │  • VibeEngineeringAgent     │    │
│                 │     │  │  • MarathonAgent            │    │
│                 │     │  │  • StreamingAgent           │    │
└─────────────────┘     │  └─────────────────────────────┘    │
                        │                                     │
                        │  ┌─────────────────────────────┐    │
                        │  │      Data Layer             │    │
                        │  │                             │    │
                        │  │  • SQLite (sessions)        │    │
                        │  │  • Redis (checkpoints)      │    │
                        │  └─────────────────────────────┘    │
                        └─────────────────────────────────────┘
                                        │
                                        ▼
                        ┌─────────────────────────────────────┐
                        │         Gemini 3 API                │
                        │                                     │
                        │  • gemini-3-pro-image-preview       │
                        │  • gemini-3-flash-preview           │
                        │  • Google Search Grounding          │
                        └─────────────────────────────────────┘
```

---

## 📁 Project Structure

```
MenuPilot/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI endpoints
│   │   │   ├── creative.py      # Creative Autopilot
│   │   │   ├── marathon.py      # Marathon Agent + WebSocket
│   │   │   ├── vibe.py          # Vibe Engineering
│   │   │   └── ...
│   │   ├── services/gemini/     # AI Agents
│   │   │   ├── base_agent.py    # Base with grounding/streaming
│   │   │   ├── creative_autopilot.py
│   │   │   ├── vibe_engineering.py
│   │   │   ├── marathon_agent.py
│   │   │   └── reasoning_agent.py
│   │   ├── core/config.py       # Settings & model configs
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   │   ├── creative/        # Campaign UI
│   │   │   ├── marathon-agent/  # Task monitor
│   │   │   └── common/          # Shared components
│   │   └── lib/api/             # API client
│   └── package.json
├── docs/
│   ├── EXECUTIVE_SUMMARY.md
│   └── MenuPilot_Deep_Analysis_Action_Plan.md
├── docker-compose.yml
└── README.md
```

---

## 🎥 Demo

[Watch the 3-minute demo video →](#)

**Demo Flow:**
1. Upload a menu image → Automatic extraction
2. Upload sales CSV → BCG Matrix analysis
3. Set location → Competitive intelligence with grounding
4. Generate campaign → 4 professional assets in 30 seconds
5. Vibe Engineering → Auto-improves quality to 85%+

---

## 🔧 Configuration

### Environment Variables

```env
# Backend (.env)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_IMAGE_GEN=gemini-3-pro-image-preview
GEMINI_MODEL_FLASH=gemini-3-flash-preview
ENABLE_GROUNDING=true
ENABLE_VIBE_ENGINEERING=true
ENABLE_MARATHON_AGENT=true
REDIS_URL=redis://localhost:6379  # Optional

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ingest/menu` | POST | Upload menu image/PDF |
| `/api/v1/analyze/bcg` | POST | Run BCG Matrix analysis |
| `/api/v1/campaigns/creative-autopilot` | POST | Generate campaign assets |
| `/api/v1/vibe-engineering/verify` | POST | Auto-verify & improve |
| `/api/v1/marathon/start` | POST | Start long-running task |
| `/api/v1/ws/marathon/{id}` | WS | Real-time progress |
| `/api/v1/analyze/competitors` | POST | Grounded competitive intel |

Full API documentation: http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Google Gemini 3** - For the incredible multimodal AI capabilities
- **Nano Banana Pro** - For text-in-image generation that actually works
- **FastAPI** - For the blazing fast Python backend
- **Next.js** - For the modern React framework

---

<div align="center">

**Built for the Gemini 3 Hackathon 2026**

Made with ❤️ by [DuqueOM](https://github.com/DuqueOM)

</div>
