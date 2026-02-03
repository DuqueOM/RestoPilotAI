"""
RestoPilotAI FastAPI Application Entry Point.

This module initializes the FastAPI application with all routes,
middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app import __version__
from app.api.routes.analysis import router as analysis_router
from app.api.routes.business import router as business_router
from app.api.routes.creative import router as creative_router
from app.api.routes.progress import router as progress_router
from app.api.routes.vibe import router as vibe_router
from app.api.routes.vibe_engineering import router as vibe_engineering_router
from app.api.routes.marathon import router as marathon_router
from app.api.routes.streaming import router as streaming_router
from app.api.routes.grounding import router as grounding_router
from app.core.config import get_settings
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    settings = get_settings()

    # Create necessary directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    (data_dir / "outputs").mkdir(exist_ok=True)
    (data_dir / "models").mkdir(exist_ok=True)

    # Initialize database
    await init_db()

    logger.info(f"RestoPilotAI started in {settings.app_env} mode")

    yield

    logger.info("RestoPilotAI shutting down")


app = FastAPI(
    title="RestoPilotAI API",
    description="""
    🍽️ **RestoPilotAI** - AI-Powered Restaurant Menu Optimization
    
    RestoPilotAI is a multimodal AI assistant that helps small and medium restaurants
    optimize their menu, pricing, and marketing campaigns using real data and
    automated reasoning powered by Google Gemini 3.
    
    ## Features
    
    - **Menu Extraction**: OCR and multimodal analysis of menu images
    - **BCG Classification**: Automatic product categorization (Star, Cash Cow, Question Mark, Dog)
    - **Sales Prediction**: ML-based forecasting for campaign scenarios
    - **Campaign Generation**: AI-generated marketing campaigns with actionable insights
    - **Thought Signatures**: Transparent reasoning with verifiable decision traces
    
    ## API Sections
    
    - `/api/v1/ingest` - Upload and process menu images and sales data
    - `/api/v1/analyze` - Run BCG analysis and generate product profiles
    - `/api/v1/predict` - Sales prediction for different scenarios
    - `/api/v1/campaigns` - Generate marketing campaign proposals
    """,
    version=__version__,
    contact={
        "name": "RestoPilotAI Team",
        "url": "https://github.com/RestoPilotAI/RestoPilotAI",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# CORS middleware for frontend integration
settings = get_settings()
# Parse origins from settings, but ensure localhost:3000 is included for dev
origins = [origin.strip() for origin in settings.cors_origins.split(",")]
if "http://localhost:3000" not in origins:
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(business_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(creative_router, prefix="/api/v1")
app.include_router(progress_router, prefix="/api/v1", tags=["WebSocket"])
app.include_router(vibe_router, prefix="/api/v1")
app.include_router(vibe_engineering_router, prefix="/api/v1")
app.include_router(marathon_router, prefix="/api/v1")
app.include_router(streaming_router, prefix="/api/v1")
app.include_router(grounding_router, prefix="/api/v1")

# Include monitoring router if available
if MONITORING_AVAILABLE and monitoring_router:
    app.include_router(monitoring_router, prefix="/api/v1")

# Serve static files for uploads if they exist
if Path("data/uploads").exists():
    app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RestoPilotAI API",
        "version": __version__,
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "gemini_model": settings.gemini_model,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and container orchestration."""
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "gemini_configured": bool(settings.gemini_api_key),
    }
