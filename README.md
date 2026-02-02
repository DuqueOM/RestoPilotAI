# 🍽️ RestoPilotAI

**AI-Powered Restaurant Optimization Suite | Powered by Gemini 3 Multimodal**

RestoPilotAI is an autonomous agentic system that helps restaurants optimize their menus, pricing, and marketing strategies using advanced multimodal AI. It leverages **Google Gemini 3** to process menu images, sales data, customer reviews, and competitor intelligence to deliver actionable insights and creative assets.

![RestoPilotAI Banner](docs/screenshots/banner_placeholder.png)

## 🚀 Key Features

### 1. 🧠 Marathon Agent (Autonomous Orchestrator)
A resilient, long-running agent that orchestrates the entire analysis pipeline.
- **Checkpoint & Recovery:** Automatically saves state every 60s to PostgreSQL. Resumes seamlessly after crashes.
- **Thought Signatures:** Transparent reasoning traces for every decision made by the AI.
- **Real-time Updates:** WebSocket integration for live progress tracking on the frontend.

### 2. ✨ Vibe Engineering (Quality Assurance)
An autonomous loop that ensures high-quality AI outputs.
- **Self-Verification:** Gemini 3 audits its own analysis (BCG, Sentiment, Predictions) before showing it to the user.
- **Auto-Improvement:** Iteratively refines results if quality thresholds aren't met.
- **Transparent Metrics:** Displays precision, completeness, and clarity scores to build user trust.

### 3. 🎨 Creative Autopilot (Nano Banana Pro)
Generates professional marketing assets using **Gemini 3 Image Generation**.
- **Multi-Format Generation:** Creates Instagram Posts (1:1), Stories (9:16), Web Banners, and Flyers.
- **Text Rendering:** Generates images with perfect, legible text in multiple languages.
- **Visual Localization:** Translates campaign assets visually (e.g., "Supreme Flavor" -> "Saveur Suprême").
- **A/B Variants:** Automatically generates creative variations (e.g., Macro Focus vs. Lifestyle) for testing.

### 4. 📍 Competitor Intelligence
- **Deep Scouting:** Finds local competitors using Google Maps & Search Grounding.
- **Menu Extraction:** converting photos of competitor menus into structured data comparisons.
- **Visual Gap Analysis:** Compares your food presentation against top local competitors.

### 5. 📊 Strategic Analysis
- **BCG Matrix 2.0:** Classifies items (Stars, Cash Cows, etc.) based on **Gross Profit** and Growth, not just revenue.
- **Sales Prediction:** XGBoost + Gemini forecasting for different scenarios (Price increase, Promo, etc.).
- **Sentiment Analysis:** Multimodal analysis of text reviews and customer photos.

## 🏗️ Architecture & Agents

RestoPilotAI is built on a multi-agent architecture where specialized AI workers collaborate to solve complex tasks.

### 1. **Marathon Agent (The Orchestrator)**
- **Role:** Project Manager & State Keeper.
- **Model:** `gemini-3-flash-preview` (High context window for state).
- **Function:** Manages the 15-step analysis pipeline. It persists state to PostgreSQL/SQLite every 60 seconds, ensuring long-running tasks (>5 mins) never lose progress even if the server restarts. It uses WebSockets to stream "Thoughts" to the frontend.

### 2. **Vibe Engineering Agent (The Auditor)**
- **Role:** Quality Assurance & Fact Checker.
- **Model:** `gemini-3-pro-preview` (High reasoning capability).
- **Function:** Recursively verifies every output from the other agents.
  - *Hallucination Check:* Verifies specific menu items exist in the uploaded images.
  - *Logic Check:* Ensures BCG classification matches the math (Margin vs. Popularity).
  - *Strategy Check:* Confirms marketing campaigns target the right "Star" products.
- **Auto-Improve:** If verification fails, it rejects the result and triggers a re-run with specific feedback.

### 3. **Creative Autopilot (The Artist)**
- **Role:** Creative Director & Designer.
- **Model:** `gemini-3-pro-image-preview` (Native image generation).
- **Function:** Generates production-ready marketing assets.
  - *Menu Transformation:* Redesigns menu layouts while preserving exact text/prices (OCR-free visual manipulation).
  - *Campaign Assets:* Creates Instagram posts and Stories with perfect embedded text (no more garbled AI text).
  - *Localization:* Visually translates assets (e.g., "Tacos" -> "Tacos Authentiques") preserving the style.

### 4. **Scout Agent (The Spy)**
- **Role:** Market Researcher.
- **Model:** `gemini-3-flash-preview` + Google Search Grounding.
- **Function:** Autonomously explores the local neighborhood.
  - *Discovery:* Finds competitors not just by keywords but by "vibe" and cuisine match.
  - *Analysis:* Scrapes public menus and social profiles to perform a "Visual Gap Analysis" against your restaurant.

---

## 🛠️ Tech Stack

- **AI Core:** Google Gemini 3 (Flash & Pro Image Preview)
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL/SQLite, WebSockets
- **Frontend:** Next.js 14, TailwindCSS, Shadcn/ui, Framer Motion
- **Infrastructure:** Docker, Background Tasks (Marathon)

---

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key (with access to Gemini 3 models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RestoPilotAI.git
   cd RestoPilotAI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY
   
   # Run server
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the App**
   Open [http://localhost:3000](http://localhost:3000)

---

## 🎥 Demo Flow

1. **Upload**: Drag & drop your menu images and sales CSV.
2. **Analysis**: Watch the Marathon Agent execute 15+ analysis stages in real-time.
3. **Verify**: See "Vibe Engineering" in action as it audits the results.
4. **Creative Studio**: Use "Creative Autopilot" to generate a campaign for your "Star" dishes.
5. **Transform**: Use the "Menu Transformation Studio" to redesign your menu style instantly.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
