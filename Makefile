# RestoPilotAI - Development Commands
# Usage: make <target>
# Version: 1.0.0

.PHONY: help setup setup-backend setup-frontend run run-backend run-frontend docker test lint clean demo typecheck

# Default Python version
PYTHON_VERSION ?= 3.11

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
NC     := \033[0m

help:
	@echo "$(CYAN)RestoPilotAI Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make setup          - Setup both backend and frontend"
	@echo "  make setup-backend  - Setup backend only (creates venv, installs deps)"
	@echo "  make setup-frontend - Setup frontend only (npm install)"
	@echo "  make setup-apikey   - Configure Gemini API key"
	@echo ""
	@echo "$(GREEN)Run:$(NC)"
	@echo "  make run            - Run both backend and frontend"
	@echo "  make run-backend    - Run backend API (port 8000)"
	@echo "  make run-frontend   - Run frontend dev server (port 3000)"
	@echo "  make demo           - Generate demo data"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker         - Build and run with Docker Compose"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "$(GREEN)Quality:$(NC)"
	@echo "  make test           - Run backend tests"
	@echo "  make typecheck      - Run TypeScript type checking"
	@echo "  make lint           - Run linters"
	@echo "  make clean          - Clean temporary files"

# ============= SETUP =============

setup: setup-backend setup-frontend
	@echo "✅ Setup complete! Run 'make run' to start the application."

setup-backend:
	@echo "📦 Setting up backend..."
	cd backend && python -m venv venv
	cd backend && . venv/bin/activate && pip install -U pip setuptools wheel
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "⚠️  Created .env - Please add your GEMINI_API_KEY"; \
	fi
	@echo "✅ Backend setup complete"

setup-frontend:
	@echo "📦 Setting up frontend..."
	cd frontend && npm install
	@echo "✅ Frontend setup complete"

setup-apikey:
	@echo "🔑 Configuring Gemini API Key..."
	@./scripts/setup_api_key.sh

# ============= RUN =============

run:
	@echo "🚀 Starting RestoPilotAI..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@make -j2 run-backend run-frontend

run-backend:
	@echo "🔧 Starting backend..."
	cd backend && /home/duque_om/miniconda3/envs/ml/bin/uvicorn app.main:app --reload --port 8000

run-frontend:
	@echo "🎨 Starting frontend..."
	cd frontend && npm run dev

# ============= DOCKER =============

docker:
	@echo "🐳 Starting with Docker Compose..."
	docker-compose up --build

docker-build:
	docker-compose build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ============= DEMO =============

demo:
	@echo "🎭 Generating demo data..."
	cd backend && . venv/bin/activate && python ../scripts/seed_demo_data.py
	@echo "✅ Demo data generated in data/demo/"

# ============= QUALITY =============

test:
	@echo "🧪 Running tests..."
	cd backend && . venv/bin/activate && pip install -q pytest pytest-asyncio httpx
	cd backend && . venv/bin/activate && pytest tests/ -v

lint:
	@echo "🔍 Running linters..."
	cd backend && . venv/bin/activate && pip install -q ruff
	cd backend && . venv/bin/activate && ruff check app/

typecheck:
	@echo "📝 Running type checks..."
	cd frontend && npm run typecheck
	@echo "✅ TypeScript check complete"

# ============= CLEAN =============

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/.ruff_cache 2>/dev/null || true
	@echo "✅ Clean complete"
