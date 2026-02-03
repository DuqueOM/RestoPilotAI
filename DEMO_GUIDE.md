# 🍹 Margarita Pinta Demo - Setup Guide

This guide explains how to run the "Margarita Pinta" demo for MenuPilot locally using Docker. This demo pre-loads a comprehensive dataset for a fully configured experience.

## Demo Features

- **Full Menu Analysis:** 137 real items extracted from the restaurant's menu (CSV).
- **Deep Sales History:** ~3 years of transaction data (63,000+ records) for accurate forecasting.
- **Strategic Insights:** BCG Matrix with granular item-level strategies (Pricing, Positioning, Priority).
- **360° Intelligence:**
  - **Competitor Analysis:** Direct and indirect competitor profiling.
  - **Sentiment Analysis:** Review mining and topic trend tracking.
  - **Sales Predictions:** 30-day revenue forecasting based on historical patterns.
- **Targeted Campaigns:** AI-generated marketing campaigns for Stars, Cash Cows, and Puzzles.

## Prerequisites

- **Docker** and **Docker Compose** installed and running.
- **Git** to clone the repository.
- A valid `.env` file (see `.env.example`).

## 🚀 Quick Start (Local)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd MenuPilot
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and add your API keys (Gemini, Google Maps, etc.).
   ```bash
   cp .env.example .env
   ```

3. **Start Services:**
   Run the application in detached mode:
   ```bash
   docker compose up -d --build
   ```

4. **Seed Demo Data:**
   Run the seeding script to populate the database with the "Margarita Pinta" dataset:
   ```bash
   # Execute inside the running backend container
   docker compose exec backend python3 scripts/seed_demo_data.py
   ```
   *Expected output: "✅ Demo data created for Margarita Pinta!"*

5. **Access the Demo:**
   - Open your browser to `http://localhost:3000`.
   - Click the **"View Live Demo (Margarita Pinta)"** button on the landing page.
   - You will be redirected to the analysis dashboard with pre-loaded insights.

## 🧪 Verification (Smoke Test)

To verify that the demo data is correctly generated and the critical paths are working, you can run the smoke test suite:

```bash
docker compose exec backend pytest tests/smoke_test_demo.py
```

## 🌐 Public Demo (Tunneling)

To share this demo publicly without a full cloud deployment, you can use **ngrok** to tunnel your localhost ports.

1. **Install ngrok:** [https://ngrok.com/download](https://ngrok.com/download)
2. **Start Tunnel:**
   ```bash
   ngrok http 3000
   ```
3. **Update Frontend Config:**
   If you want the public URL to work seamlessly, ensure `NEXT_PUBLIC_API_URL` in your `.env` points to your public backend URL (you might need a second tunnel for port 8000 or configure ngrok to route both).
   
   *Simpler approach:* Just share the ngrok URL for port 3000. Note that the frontend will try to contact `localhost:8000` by default (client-side). For a true public demo, you need both accessible or a reverse proxy.

## 🛠️ Troubleshooting

- **"Demo data not found":** Ensure you ran step 4 (`seed_demo_data.py`).
- **Docker Connection Refused:** Make sure your Docker Daemon is running.
- **API Errors:** Check `docker compose logs backend` for details.
