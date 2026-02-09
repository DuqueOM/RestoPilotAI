# RestoPilotAI Backend - Production Dockerfile

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# First: CPU-only PyTorch (saves ~1.5GB vs full CUDA version — Cloud Run has no GPU)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels torch torchvision \
       --index-url https://download.pytorch.org/whl/cpu

# Then: remaining dependencies (excluding torch/torchvision already handled above)
COPY requirements.txt .
RUN grep -v -E "^(torch|torchvision)" requirements.txt > requirements_no_torch.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements_no_torch.txt

# Production image
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# Install runtime dependencies (including Tesseract for OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY app /app/app
COPY .env.example /app/.env.example

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/outputs /app/data/models /app/data/demo

# Copy demo data for hackathon judges (exclude large source CSVs)
COPY data/demo/*.json /app/data/demo/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_ENV=production

# Cloud Run injects PORT env var; default to 8000 for local
ENV PORT=8000
EXPOSE ${PORT}

# Health check (local Docker only; Cloud Run uses its own probes)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health')" || exit 1

# Run the application — Cloud Run sets PORT dynamically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
