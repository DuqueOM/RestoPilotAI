"""Monitoring endpoints for Gemini API usage and health.

Provides real-time visibility into:
- Rate limiting status
- Cost tracking
- Model health and fallback status
- Token usage statistics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.core.rate_limiter import get_rate_limiter
from app.core.model_fallback import get_fallback_handler

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/gemini/usage")
async def get_gemini_usage() -> Dict[str, Any]:
    """
    Get current Gemini API usage statistics.
    
    Returns:
        Usage stats including rate limits, costs, and token consumption
    """
    try:
        limiter = get_rate_limiter()
        stats = limiter.get_usage_stats()
        
        return {
            "status": "ok",
            "timestamp": limiter.calls_today[-1].timestamp if limiter.calls_today else None,
            "rate_limiting": {
                "requests_in_window": stats["requests_in_window"],
                "rpm_limit": stats["rpm_limit"],
                "rpm_usage_pct": round(
                    (stats["requests_in_window"] / stats["rpm_limit"]) * 100, 2
                ),
                "tokens_in_window": stats["tokens_in_window"],
                "tpm_limit": stats["tpm_limit"],
                "tpm_usage_pct": round(
                    (stats["tokens_in_window"] / stats["tpm_limit"]) * 100, 2
                ),
            },
            "cost_tracking": {
                "daily_cost_usd": stats["daily_cost_usd"],
                "budget_limit_usd": stats["budget_limit_usd"],
                "budget_remaining_usd": stats["budget_remaining_usd"],
                "budget_usage_pct": round(
                    (stats["daily_cost_usd"] / stats["budget_limit_usd"]) * 100, 2
                ),
                "budget_exceeded": stats["budget_exceeded"],
            },
            "token_usage": {
                "calls_today": stats["calls_today"],
                "total_input_tokens_today": stats["total_input_tokens_today"],
                "total_output_tokens_today": stats["total_output_tokens_today"],
                "total_tokens_today": (
                    stats["total_input_tokens_today"] + 
                    stats["total_output_tokens_today"]
                ),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.get("/gemini/models")
async def get_model_health() -> Dict[str, Any]:
    """
    Get health status of all Gemini models.
    
    Returns:
        Health stats for each model including success rates and failure counts
    """
    try:
        handler = get_fallback_handler()
        model_stats = handler.get_model_stats()
        
        return {
            "status": "ok",
            "models": model_stats,
            "summary": {
                "total_models": len(model_stats),
                "healthy_models": sum(
                    1 for stats in model_stats.values()
                    if stats["health"] == "healthy"
                ),
                "degraded_models": sum(
                    1 for stats in model_stats.values()
                    if stats["health"] == "degraded"
                ),
                "failed_models": sum(
                    1 for stats in model_stats.values()
                    if stats["health"] == "failed"
                ),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model health: {str(e)}")


@router.get("/gemini/health")
async def health_check() -> Dict[str, Any]:
    """
    Combined health check for Gemini API integration.
    
    Returns:
        Overall health status with key metrics
    """
    try:
        limiter = get_rate_limiter()
        handler = get_fallback_handler()
        
        usage_stats = limiter.get_usage_stats()
        model_stats = handler.get_model_stats()
        
        # Determine overall health
        budget_ok = not usage_stats["budget_exceeded"]
        models_ok = any(
            stats["health"] == "healthy"
            for stats in model_stats.values()
        )
        
        overall_health = "healthy" if (budget_ok and models_ok) else "degraded"
        if usage_stats["budget_exceeded"]:
            overall_health = "critical"
        
        return {
            "status": overall_health,
            "checks": {
                "budget": "ok" if budget_ok else "exceeded",
                "models": "ok" if models_ok else "all_failed",
                "rate_limit": "ok" if usage_stats["requests_in_window"] < usage_stats["rpm_limit"] else "throttled",
            },
            "metrics": {
                "budget_remaining_usd": usage_stats["budget_remaining_usd"],
                "healthy_models": sum(
                    1 for stats in model_stats.values()
                    if stats["health"] == "healthy"
                ),
                "requests_available": max(
                    0,
                    usage_stats["rpm_limit"] - usage_stats["requests_in_window"]
                ),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/gemini/reset-daily-stats")
async def reset_daily_stats() -> Dict[str, str]:
    """
    Reset daily statistics (admin endpoint).
    
    Returns:
        Confirmation message
    """
    try:
        limiter = get_rate_limiter()
        limiter.reset_daily_stats()
        
        return {
            "status": "ok",
            "message": "Daily statistics reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset stats: {str(e)}")
