# 🚀 MenuPilot - Quick Start Guide

## Prerequisites

- Python 3.11 or 3.12 (recommended)
- Node.js 18+
- [Gemini API Key](https://aistudio.google.com/apikey) (free)

## 1️⃣ Get Your API Key

1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

## 2️⃣ Setup (Choose One Method)

### Method A: Automated Setup (Recommended)

```bash
# Clone and navigate
git clone https://github.com/DuqueOM/MenuPilot.git
cd MenuPilot

# Configure API key
./scripts/setup_api_key.sh

# Install everything
make setup

# Run!
make run
```

### Method B: Manual Setup

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

### Method C: Docker (Easiest)

```bash
export GEMINI_API_KEY=your_key_here
docker-compose up --build
```

## 3️⃣ Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 4️⃣ Test It Out

1. **Upload Menu**: Drag & drop a menu image or PDF
2. **Upload Sales Data** (optional): CSV with columns: `item_name`, `date`, `quantity_sold`
3. **Run Analysis**: Click "Run Analysis"
4. **View Results**: BCG matrix, predictions, campaigns

## 📄 Supported File Formats

- **Menu**: JPG, PNG, WEBP, **PDF** ✨
- **Dish Photos**: JPG, PNG, WEBP
- **Sales Data**: CSV, XLSX

## ⚠️ Troubleshooting

### "API key not valid" Error

```bash
# Check if API key is set
cat backend/.env | grep GEMINI_API_KEY

# If empty or wrong, run:
./scripts/setup_api_key.sh
```

### PDF Not Processing

```bash
# Install PDF dependencies
cd backend
source venv/bin/activate
pip install pdf2image PyMuPDF

# Linux: Install poppler-utils
sudo apt-get install poppler-utils

# macOS: Install poppler
brew install poppler
```

### Python Version Issues

```bash
# Use Python 3.11 or 3.12
conda create -n menupilot python=3.11 -y
conda activate menupilot
cd backend
pip install -r requirements.txt
```

## 🎯 Example Workflow

1. **Menu Upload**: Upload `menu.pdf` → Extracts 15 items
2. **Sales Upload**: Upload `sales.csv` → Loads historical data
3. **Analysis**: Runs BCG classification
4. **Predictions**: Forecasts next 14 days
5. **Campaigns**: Generates 3 marketing proposals

## 📚 More Information

- [Full README](README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)

## 💡 Tips

- Use high-quality images for better extraction
- PDFs work great for digital menus
- Sales data improves prediction accuracy
- Try different thinking levels (Quick/Standard/Deep/Exhaustive)

---

**Need help?** Open an issue on GitHub or check the documentation.
