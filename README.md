# 🧠 RestoPilotAI

> **Intelligence That Sees, Hears, and Thinks Like a Consultant.**
>
> An autonomous, multimodal market intelligence agent for the restaurant industry, powered by **Google Gemini 3**.

[![Powered by Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tech Stack: FastAPI + Next.js](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20Docker-success?style=for-the-badge&logo=docker)]()
[![Status: Operational](https://img.shields.io/badge/Status-Operational-green?style=for-the-badge)]()

---

## 🚀 The Vision

RestoPilotAI replaces expensive, slow consultancy with an **Autonomous AI Agent** that works in real-time. By simply providing a location, the system orchestrates a fleet of specialized AI agents to:

1.  **Scout** the neighborhood and competitors physically and digitally.
2.  **See** and critique food presentation using computer vision.
3.  **Listen** to business owners' verbal context and goals.
4.  **Predict** sales trends using machine learning (XGBoost).
5.  **Strategize** actionable marketing campaigns based on BCG matrix analysis.

No spreadsheets. No manual data entry. Just actionable intelligence generated in minutes.

---

## 🌟 Key Capabilities (Verified & Implemented)

### 1. 🤖 Multimodal "Marathon Agent" Orchestrator
At the core is a state-managed orchestrator (`AnalysisOrchestrator`) that runs a resilient 9-stage analysis pipeline. It is not a simple linear script but a persistent workflow engine that maintains context, handles failures, and manages state across:
- **Location & Demographics Analysis**
- **Competitor Discovery & Enrichment**
- **Multimodal Content Processing (Audio/Image)**
- **Strategic Verification Loops**

### 2. 👁️ Gemini 3 Vision: "The Food Critic"
We don't just scrape text; we analyze the *visual* appeal of the market using **Gemini 3's native multimodal capabilities**.
- **Visual Gap Analysis**: The agent downloads competitor menu photos and uses Gemini Vision to score them on lighting, plating, and "appetite appeal".
- **Aesthetic Benchmarking**: Identifies the visual style (colors, vibe) winning in the local market.
- **Dish Video Analysis**: Capable of processing video content to understand dynamic food presentation.

### 3. 👂 Audio-Native Context Injection
Business isn't just data; it's about the owner's story.
- **Voice-to-Strategy**: Owners can record voice notes about their history, values, or challenges.
- **Semantic Integration**: The `ContextProcessor` transcribes audio and injects these qualitative insights directly into quantitative models (e.g., adjusting campaign tone based on the owner's actual voice and values).

### 4. 🕵️ Autonomous Scout & Social Intelligence
- **Deep Competitor Profiling**: Integrates **Google Places API (New)** for verified business data, reviews, and operational details.
- **Social Reconnaissance**: Uses a custom `SocialScraper` (powered by Instaloader) to extract real engagement metrics, hashtags, and visual trends from public Instagram profiles.
- **Neighborhood Vibe**: Analyzes the surrounding area for demand drivers (offices, universities, nightlife) to determine the "Urban Personality" of the location.

### 5. 📈 Hybrid Intelligence (AI + ML)
We combine Generative AI with traditional Machine Learning for precision:
- **Sales Prediction Engine**: Uses **XGBoost** to forecast sales trends based on historical data, pricing, seasonality, and local events.
- **BCG Matrix Classification**: Automatically categorizes menu items into **Stars**, **Cash Cows**, **Dogs**, and **Question Marks**.
- **Strategic Campaign Generator**: Synthesizes ML predictions + BCG data + Owner Context to generate ready-to-launch marketing campaigns (social posts, emails, in-store promos).

---

## 🏗️ Technical Architecture

The project follows a modern **Agentic Microservices** architecture:

### **Backend (`/backend`)**
Built with **Python 3.11** and **FastAPI**.
*   **Intelligence Layer**:
    *   `ScoutAgent`: Geospatial discovery & data enrichment.
    *   `ContextProcessor`: Gemini 3 Audio/Text processing.
    *   `VisualGapAnalyzer`: Gemini 3 Vision analysis.
    *   `SalesPredictor`: Scikit-learn/XGBoost forecasting pipelines.
    *   `MenuExtractor`: Hybrid OCR + Gemini Vision for PDF/Image menu digitizing.
*   **Infrastructure**:
    *   **Redis**: Caching & Task Queues for async agent operations.
    *   **PostgreSQL**: Structured data persistence (AsyncPG).
    *   **Docker**: Containerized deployment.

### **Frontend (`/frontend`)**
Built with **Next.js 14 (App Router)** and **TypeScript**.
*   **Thinking Stream**: Real-time WebSocket connection visualizing the agent's "thought process" as it works (Chain-of-Thought visualization).
*   **Progressive UX**: A vertical, conversational flow that reveals insights step-by-step, mimicking a consultant interview.
*   **Interactive Dashboards**: Dynamic charts (Recharts) and Google Maps integration for spatial data.

---

## 🛠️ Getting Started

### **Option A: Quick Start (Docker)**
The easiest way to run the full stack (Backend, Frontend, DB, Redis).

```bash
# 1. Environment Setup
cp .env.example .env
# Edit .env: Add GEMINI_API_KEY and GOOGLE_PLACES_API_KEY

# 2. Launch
docker-compose up --build
```
Access the app at `http://localhost:3000`.

### **Option B: Manual Development**

**Backend:**
See [backend/README.md](./backend/README.md) for detailed setup.
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*Docs available at: `http://localhost:8000/docs`*

**Frontend:**
See [frontend/README.md](./frontend/README.md) for detailed setup.
```bash
cd frontend
npm install
npm run dev
```

---

## 🧠 Why Gemini 3?

RestoPilotAI was built specifically to exploit the **native multimodal** capabilities of Gemini 3:

| Feature | Legacy AI Approach | RestoPilotAI (Gemini 3) |
| :--- | :--- | :--- |
| **Input** | Text/CSV only | **Audio, Images, Video, Text** |
| **Context** | Short context window | **Long Context (Full PDF Menus + History)** |
| **Reasoning** | Single-shot answers | **Chain-of-Thought "Thinking" Loops** |
| **Speed** | Slow, multi-model piping | **Native Multimodal Latency** |

---

## 📜 License
MIT License. Built for the Gemini 3 Developer Competition.
