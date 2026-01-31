"""
Structured Logging Configuration for RestoPilotAI.

Provides:
- Structured JSON logging for production
- Human-readable format for development
- Context-aware logging with correlation IDs
- Gemini API call tracking
- Performance metrics logging
"""

import contextvars
import json
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar
from uuid import uuid4

from loguru import logger

# Context variables for request tracking
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "session_id", default=""
)
user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="")


@dataclass
class LogContext:
    """Context for structured logging."""

    request_id: str = ""
    session_id: str = ""
    user_id: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "request_id": self.request_id or request_id_var.get(),
            "session_id": self.session_id or session_id_var.get(),
            "user_id": self.user_id or user_id_var.get(),
        }
        result.update(self.extra)
        return {k: v for k, v in result.items() if v}


def json_serializer(record: Dict[str, Any]) -> str:
    """Serialize log record to JSON."""

    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add extra context
    if record.get("extra"):
        subset.update(record["extra"])

    # Add exception info
    if record.get("exception"):
        subset["exception"] = {
            "type": (
                record["exception"].type.__name__ if record["exception"].type else None
            ),
            "value": (
                str(record["exception"].value) if record["exception"].value else None
            ),
            "traceback": (
                record["exception"].traceback if record["exception"].traceback else None
            ),
        }

    return json.dumps(subset, default=str)


def human_format(record: Dict[str, Any]) -> str:
    """Format log record for human readability."""

    level = record["level"].name
    time_str = record["time"].strftime("%H:%M:%S.%f")[:-3]
    message = record["message"]

    # Color coding based on level
    level_colors = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    reset = "\033[0m"
    color = level_colors.get(level, "")

    base = f"{time_str} | {color}{level:8}{reset} | {message}"

    # Add extra context if present
    extra = record.get("extra", {})
    if extra:
        context_parts = []
        for key, value in extra.items():
            if key not in ("request_id", "session_id", "user_id"):
                context_parts.append(f"{key}={value}")
        if context_parts:
            base += f" | {', '.join(context_parts)}"

    return base + "\n"


def configure_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Whether to output JSON format (for production)
        log_file: Optional file path for log output
    """
    # Remove default handler
    logger.remove()

    # Console output
    if json_output:
        logger.add(
            sys.stdout,
            format="{extra}",
            serialize=True,
            level=level,
        )
    else:
        logger.add(
            sys.stdout,
            format=human_format,
            level=level,
            colorize=True,
        )

    # File output if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {module}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            level=level,
        )

    logger.info(
        "Logging configured",
        level=level,
        json_output=json_output,
        log_file=log_file,
    )


def get_logger(name: str = "RestoPilotAI") -> "logger":
    """Get a logger instance with optional context binding."""
    return logger.bind(component=name)


@contextmanager
def log_context(**kwargs):
    """Context manager for adding temporary logging context."""

    tokens = {}

    if "request_id" in kwargs:
        tokens["request_id"] = request_id_var.set(kwargs.pop("request_id"))
    if "session_id" in kwargs:
        tokens["session_id"] = session_id_var.set(kwargs.pop("session_id"))
    if "user_id" in kwargs:
        tokens["user_id"] = user_id_var.set(kwargs.pop("user_id"))

    with logger.contextualize(**kwargs):
        try:
            yield
        finally:
            for name, token in tokens.items():
                if name == "request_id":
                    request_id_var.reset(token)
                elif name == "session_id":
                    session_id_var.reset(token)
                elif name == "user_id":
                    user_id_var.reset(token)


T = TypeVar("T")


def log_execution_time(
    operation: str = "",
    log_args: bool = False,
    log_result: bool = False,
):
    """Decorator to log function execution time."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            op_name = operation or func.__name__
            start_time = time.time()

            log_data = {"operation": op_name}
            if log_args:
                log_data["args_count"] = len(args)
                log_data["kwargs_keys"] = list(kwargs.keys())

            logger.debug(f"Starting {op_name}", **log_data)

            try:
                result = await func(*args, **kwargs)

                elapsed_ms = int((time.time() - start_time) * 1000)
                log_data["duration_ms"] = elapsed_ms
                log_data["status"] = "success"

                if log_result and result:
                    if isinstance(result, dict):
                        log_data["result_keys"] = list(result.keys())
                    elif isinstance(result, (list, tuple)):
                        log_data["result_count"] = len(result)

                logger.info(f"Completed {op_name}", **log_data)

                return result

            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                log_data["duration_ms"] = elapsed_ms
                log_data["status"] = "error"
                log_data["error_type"] = type(e).__name__
                log_data["error_message"] = str(e)[:200]

                logger.error(f"Failed {op_name}", **log_data)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            op_name = operation or func.__name__
            start_time = time.time()

            log_data = {"operation": op_name}

            try:
                result = func(*args, **kwargs)

                elapsed_ms = int((time.time() - start_time) * 1000)
                log_data["duration_ms"] = elapsed_ms

                logger.info(f"Completed {op_name}", **log_data)

                return result

            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                log_data["duration_ms"] = elapsed_ms
                log_data["error"] = str(e)[:200]

                logger.error(f"Failed {op_name}", **log_data)
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class GeminiLogger:
    """
    Specialized logger for Gemini API calls.

    Tracks:
    - Request/response patterns
    - Token usage
    - Latency metrics
    - Cost estimation
    - Error patterns
    """

    def __init__(self, agent_name: str = "gemini"):
        self.agent_name = agent_name
        self.logger = get_logger(f"gemini.{agent_name}")

    def log_request(
        self,
        feature: str,
        model: str,
        prompt_tokens: int = 0,
        estimated_output_tokens: int = 0,
        **extra,
    ) -> str:
        """Log start of Gemini request, return request ID."""
        request_id = str(uuid4())[:8]

        self.logger.info(
            "gemini_request_start",
            request_id=request_id,
            agent=self.agent_name,
            feature=feature,
            model=model,
            prompt_tokens=prompt_tokens,
            estimated_output_tokens=estimated_output_tokens,
            **extra,
        )

        return request_id

    def log_response(
        self,
        request_id: str,
        feature: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        success: bool = True,
        cached: bool = False,
        error: Optional[str] = None,
        **extra,
    ) -> None:
        """Log completion of Gemini request."""

        # Estimate cost (Gemini 2.0 Flash pricing)
        cost_usd = (input_tokens / 1_000_000 * 0.10) + (
            output_tokens / 1_000_000 * 0.40
        )

        log_data = {
            "request_id": request_id,
            "agent": self.agent_name,
            "feature": feature,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": round(cost_usd, 6),
            "cached": cached,
            "success": success,
            **extra,
        }

        if error:
            log_data["error"] = error[:200]
            self.logger.error("gemini_request_failed", **log_data)
        else:
            self.logger.info("gemini_request_complete", **log_data)

    def log_cache_hit(self, feature: str, cache_key: str) -> None:
        """Log cache hit for Gemini response."""
        self.logger.debug(
            "gemini_cache_hit",
            agent=self.agent_name,
            feature=feature,
            cache_key=cache_key[:16],
        )

    def log_rate_limit(self, wait_seconds: float) -> None:
        """Log rate limit wait."""
        self.logger.warning(
            "gemini_rate_limit",
            agent=self.agent_name,
            wait_seconds=wait_seconds,
        )

    def log_retry(self, attempt: int, max_attempts: int, error: str) -> None:
        """Log retry attempt."""
        self.logger.warning(
            "gemini_retry",
            agent=self.agent_name,
            attempt=attempt,
            max_attempts=max_attempts,
            error=error[:100],
        )


class MetricsLogger:
    """
    Logger for application metrics and analytics.

    Tracks:
    - Pipeline execution metrics
    - User engagement
    - Feature usage
    - Performance benchmarks
    """

    def __init__(self):
        self.logger = get_logger("metrics")

    def log_pipeline_start(self, session_id: str, stages: list) -> None:
        """Log pipeline execution start."""
        self.logger.info(
            "pipeline_start",
            session_id=session_id,
            stages=stages,
            stage_count=len(stages),
        )

    def log_pipeline_stage(
        self,
        session_id: str,
        stage: str,
        duration_ms: int,
        success: bool,
        items_processed: int = 0,
        **extra,
    ) -> None:
        """Log individual pipeline stage completion."""
        self.logger.info(
            "pipeline_stage",
            session_id=session_id,
            stage=stage,
            duration_ms=duration_ms,
            success=success,
            items_processed=items_processed,
            **extra,
        )

    def log_pipeline_complete(
        self,
        session_id: str,
        total_duration_ms: int,
        stages_completed: int,
        total_tokens: int,
        total_cost_usd: float,
    ) -> None:
        """Log pipeline completion."""
        self.logger.info(
            "pipeline_complete",
            session_id=session_id,
            total_duration_ms=total_duration_ms,
            stages_completed=stages_completed,
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost_usd, 4),
        )

    def log_feature_usage(self, feature: str, user_id: str = "", **extra) -> None:
        """Log feature usage for analytics."""
        self.logger.info(
            "feature_usage",
            feature=feature,
            user_id=user_id or user_id_var.get(),
            **extra,
        )

    def log_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: int,
        **extra,
    ) -> None:
        """Log API request metrics."""
        self.logger.info(
            "api_request",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            request_id=request_id_var.get(),
            **extra,
        )


# Global instances
gemini_logger = GeminiLogger()
metrics_logger = MetricsLogger()


def setup_request_logging():
    """
    FastAPI middleware setup for request logging.

    Usage in main.py:
        from app.core.logging_config import setup_request_logging
        setup_request_logging(app)
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request_id = str(uuid4())
            request_id_var.set(request_id)

            start_time = time.time()

            response = await call_next(request)

            duration_ms = int((time.time() - start_time) * 1000)

            metrics_logger.log_api_request(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            response.headers["X-Request-ID"] = request_id

            return response

    return RequestLoggingMiddleware
