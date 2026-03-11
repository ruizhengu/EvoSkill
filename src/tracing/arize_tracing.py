"""Phoenix tracing integration for EvoSkill.

This module provides tracing capabilities using Phoenix (open-source Arize).
It records LLM calls with metadata like model, tokens, latency, and tool calls.

Environment variables:
    PHOENIX_ENDPOINT: Phoenix server endpoint (e.g., http://localhost:6006)
    PHOENIX_API_KEY: Optional API key for Phoenix cloud
    PHOENIX_PROJECT: Project name (default: evoskill)
    ARIZE_TRACE_ENABLED: Set to "true" to enable tracing
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

logger = logging.getLogger(__name__)

# Global tracer state
_tracer_initialized = False
_tracer: Optional[Any] = None


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled via environment variables."""
    # Check for explicit enable flag or Phoenix endpoint
    if os.environ.get("ARIZE_TRACE_ENABLED", "").lower() == "true":
        return True
    if os.environ.get("PHOENIX_ENDPOINT"):
        return True
    return False


def get_project_name() -> str:
    """Get the Phoenix project name from environment or default."""
    return os.environ.get("PHOENIX_PROJECT", "evoskill")


def init_tracer() -> bool:
    """Initialize the Phoenix tracer.

    Returns:
        True if tracer was initialized successfully, False otherwise.
    """
    global _tracer_initialized, _tracer

    if _tracer_initialized:
        return _tracer is not None

    # Check if we have Phoenix configuration
    endpoint = os.environ.get("PHOENIX_ENDPOINT")
    api_key = os.environ.get("PHOENIX_API_KEY")

    if not endpoint and not api_key:
        # Try Arize cloud configuration as fallback
        api_key = os.environ.get("ARIZE_API_KEY")
        space_id = os.environ.get("ARIZE_SPACE_ID")
        if api_key and space_id:
            # Use Arize cloud
            endpoint = f"https://app.phoenix.arize.com"

    # If ARIZE_TRACE_ENABLED is set, we still want to initialize (even without endpoint)
    trace_enabled = os.environ.get("ARIZE_TRACE_ENABLED", "").lower() == "true"
    if not endpoint and not api_key and not trace_enabled:
        logger.warning(
            "Phoenix tracing disabled: PHOENIX_ENDPOINT or PHOENIX_API_KEY not set"
        )
        _tracer_initialized = True
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource

        # Create a resource with the project name
        resource = Resource.create({
            "service.name": get_project_name(),
        })

        # Create and set the tracer provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # Get the tracer
        _tracer = trace.get_tracer("evoskill")

        # Try to set up a simple console exporter for debugging
        # Real implementation would use OTLP exporter to Phoenix
        logger.info(
            f"Phoenix tracing initialized: project={get_project_name()}, endpoint={endpoint or 'console only'}"
        )
        _tracer_initialized = True
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize tracer: {e}")
        _tracer_initialized = True
        _tracer = None
        return False


def get_tracer() -> Any:
    """Get the initialized tracer.

    Returns:
        The OpenTelemetry tracer, or None if not initialized.
    """
    global _tracer_initialized
    if not _tracer_initialized:
        init_tracer()
    return _tracer


@asynccontextmanager
async def trace_agent_call(
    query: str,
    model: str,
    tools: list[str],
) -> AsyncGenerator[dict[str, Any], None]:
    """Context manager for tracing an agent call.

    Args:
        query: The user query
        model: Model being used
        tools: List of available tools

    Yields:
        A dictionary that should be updated with call results
    """
    tracer = get_tracer()

    if tracer is None:
        # Tracing not available, yield dummy context
        yield {
            "success": False,
            "error": "tracer not initialized",
        }
        return

    # Create a span
    with tracer.start_as_current_span("agent_call") as span:
        # Set span attributes
        span.set_attribute("evoskill.query_length", len(query))
        span.set_attribute("evoskill.model", model)
        span.set_attribute("evoskill.tools_count", len(tools))
        span.set_attribute("evoskill.tools", ", ".join(tools))

        result_data = {
            "success": True,
            "span": span,
        }

        try:
            yield result_data
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            result_data["success"] = False
            result_data["error"] = str(e)
            raise
        finally:
            # Additional attributes can be set after the call
            pass


def record_trace_result(
    span: Any,
    duration_ms: int,
    total_cost_usd: float,
    usage: dict[str, Any],
    result: str,
    is_error: bool,
    output: Optional[Any] = None,
) -> None:
    """Record trace result metadata to the span.

    Args:
        span: The OpenTelemetry span
        duration_ms: Call duration in milliseconds
        total_cost_usd: Total cost in USD
        usage: Token usage dict
        result: Result text
        is_error: Whether the call resulted in an error
        output: Optional structured output
    """
    if span is None:
        return

    span.set_attribute("evoskill.duration_ms", duration_ms)
    span.set_attribute("evoskill.cost_usd", total_cost_usd)

    if usage:
        span.set_attribute(
            "evoskill.input_tokens", usage.get("input_tokens", 0)
        )
        span.set_attribute(
            "evoskill.output_tokens", usage.get("output_tokens", 0)
        )
        span.set_attribute(
            "evoskill.total_tokens", usage.get("total_tokens", 0)
        )

    if result:
        span.set_attribute("evoskill.result_length", len(result))

    if is_error:
        span.set_attribute("error", True)

    if output:
        span.set_attribute("evoskill.has_structured_output", True)
