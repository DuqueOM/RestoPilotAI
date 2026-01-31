# 🍽️ RestoPilotAI

**AI-Powered Competitive Intelligence & Menu Optimization for Restaurants**

[![Powered by Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status: Hackathon Ready](https://img.shields.io/badge/Status-Hackathon%20Ready-success?style=for-the-badge)]()

> **"Give us your address. We'll give you competitive intelligence that would cost $5,000 and 2 months with a consultant."**

RestoPilotAI is an autonomous AI intelligence platform that uses **Google Gemini 3's multimodal capabilities** to gather, analyze, and synthesize competitive data for restaurants. No spreadsheets. No manual research. Just your location—and our Agents do the rest.

---

## 🎯 The Problem We Solve

**Traditional Competitive Analysis:**
- ❌ Hire consultant: $5,000+
- ❌ Wait 2 months for report
- ❌ Manual data collection from dozens of sources
- ❌ Static insights, outdated by publication

**RestoPilotAI:**
- ✅ Enter your address: Instant Start
- ✅ **Real-time Agentic Analysis** in < 5 minutes
- ✅ **Scout Agent** autonomously gathers data from Google Maps, Instagram, reviews, and menus
- ✅ **Multimodal Vision** analyzes dish quality, ambiance, and social aesthetic
- ✅ **Live Thinking Stream** shows the AI's reasoning process as it happens

---

## 🌟 Key Features

### **1. Autonomous Intelligence Gathering ("Scout Agent 2.0")**
Unlike traditional tools where you input data manually, RestoPilotAI's **Scout Agent** acts as an autonomous field researcher:
- **Geospatial Discovery**: Integrates with Google Maps/Places API to identify relevant competitors within a dynamic radius.
- **Neighborhood Profiling**: Analyzes nearby businesses (universities, offices) to determine demographic opportunities.
- **Social Intelligence**: Uses `SocialScraper` to extract and analyze Instagram content (captions + images) for aesthetic and engagement benchmarking.

### **2. True Multimodal Intelligence (Gemini 3 Vision)**
We don't just read text. We see what your customers see:
- **📸 Visual Gap Analysis**: Compares your dish photography against competitors using high-resolution vision. Scores lighting, composition, and "appetite appeal".
- **🍽️ Menu Extraction**: Extracts items, prices, and descriptions from raw menu photos or PDFs.
- **🎨 Aesthetic Benchmarking**: Analyzes color palettes and filter styles of top-performing competitors.

### **3. Strategic Business Intelligence**
- **Enhanced BCG Matrix**: Combines sales data with visual quality scores and sentiment to classify items (Star, Cash Cow, Dog, Question Mark).
- **Price Elasticity**: Estimates price sensitivity based on neighborhood demographics and competitor positioning.
- **Campaign Generation**: Synthesizes all intelligence to generate actionable marketing campaigns (e.g., "Student Tuesday" based on university proximity).

### **4. Real-Time Reasoning Engine**
- **Thinking Stream UI**: Watch the AI "think" in real-time via WebSockets. See it formulate hypotheses, verify data, and cross-reference sources.
- **Marathon Agent Architecture**: Orchestrates a 9-stage analysis pipeline with fault tolerance and state persistence.

---

## 🏗️ Technical Architecture

RestoPilotAI relies on a robust **Agentic Architecture** powered by FastAPI and Next.js.

### **Backend (`/backend`)**
- **Framework**: FastAPI (Python 3.11+)
- **Core Agents**:
  - `AnalysisOrchestrator`: Manages the full pipeline state.
  - `ScoutAgent`: Discovers and enriches location/competitor data.
  - `CompetitorIntelligenceService`: Price comparison & menu analysis.
  - `VisualGapAnalyzer`: Gemini Vision aesthetic comparison.
  - `NeighborhoodAnalyzer`: Demographic & traffic analysis.
  - `SocialScraper`: Instagram data extraction.
- **AI Engine**: Google Gemini 3 (Flash & Pro) via `google-genai`.
- **Infrastructure**:
  - WebSocketManager for real-time streaming.
  - Async/Await for parallel agent execution.
  - Pydantic for strict schema validation.

### **Frontend (`/frontend`)**
- **Framework**: Next.js 14 (App Router)
- **UI/UX**:
  - **Vertical Progressive Flow**: Conversational, step-by-step interface.
  - **ThinkingStream**: Real-time visualization of backend agent thought traces.
  - **Interactive Dashboards**: Recharts for data visualization, Google Maps integration.
- **Styling**: Tailwind CSS, Lucide Icons, Shadcn/UI.

### **Pipeline Stages**
1. **Ingestion**: Upload images/CSV or define location.
2. **Scout**: Geocode -> Find Competitors -> Profile Neighborhood.
3. **Menu Extraction**: OCR + Multimodal parsing.
4. **Competitor Analysis**: Scraping -> Price Comparison.
5. **Visual Analysis**: Dish scoring -> Gap identification.
6. **Sentiment**: Review analysis.
7. **Business Logic**: Sales prediction -> BCG Matrix.
8. **Strategy**: Campaign generation.
9. **Verification**: "Vibe Check" self-correction loop.

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- Google Gemini API Key
- Google Maps/Places API Key (Optional, mocks available)

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/DuqueOM/RestoPilotAI.git
   cd RestoPilotAI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   
   # Configure Environment
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   
   # Run Server
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Run Client
   npm run dev
   ```

4. **Access**
   - Frontend: `http://localhost:3000`
   - Backend Docs: `http://localhost:8000/docs`

---

## 🧠 How Gemini 3 Powers RestoPilotAI

RestoPilotAI showcases the advanced capabilities of Gemini 3:

| Feature | Gemini Capability | Implementation |
|---------|-------------------|----------------|
| **Visual Gap Analyzer** | Multimodal Vision | Analyzes dish plating, lighting, and composition to score "Instagram-worthiness". |
| **Scout Agent** | Function Calling | Autonomously calls Maps/Search APIs to find and filter relevant competitors. |
| **Extraction Engine** | Long Context Window | Processes full PDF menus and dozens of social posts in a single pass. |
| **Reasoning Stream** | Chain-of-Thought | Generates transparent "thought traces" to explain strategic recommendations. |

---

## 🏆 Hackathon Status

**Completed Modules:**
- [x] **Geocoding & Places**: Google Maps integration + Mock fallbacks.
- [x] **Scout Agent**: Autonomous discovery & enrichment.
- [x] **Social Intelligence**: Real Instagram scraping & analysis.
- [x] **Visual AI**: High-res dish analysis.
- [x] **Orchestrator**: 9-stage resilient pipeline.
- [x] **Real-time UI**: WebSocket streaming & Thinking components.
- [x] **Documentation**: Comprehensive architecture guide.

---

## 📜 License

MIT License - See [LICENSE](./LICENSE) for details.

---

**Built with ❤️ by the RestoPilotAI Team for the Gemini 3 Hackathon.**
