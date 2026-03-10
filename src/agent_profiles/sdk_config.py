"""SDK configuration and selection logic.

This module provides a global setting to choose between claude-agent-sdk and opencode-ai.
"""

import os
from typing import Literal

SDKType = Literal["claude", "opencode"]

# Global SDK selection (can be overridden via CLI arguments)
_current_sdk: SDKType = "claude"

# Custom environment variables for API configuration
_custom_api_key: str | None = None
_custom_auth_token: str | None = None
_custom_base_url: str | None = None


def set_sdk(sdk: SDKType) -> None:
    """Set the current SDK to use globally."""
    global _current_sdk
    if sdk not in ("claude", "opencode"):
        raise ValueError(f"Invalid SDK type: {sdk}. Must be 'claude' or 'opencode'")
    _current_sdk = sdk


def get_sdk() -> SDKType:
    """Get the currently configured SDK."""
    return _current_sdk


def is_claude_sdk() -> bool:
    """Check if claude-agent-sdk is the current SDK."""
    return _current_sdk == "claude"


def is_opencode_sdk() -> bool:
    """Check if opencode-ai is the current SDK."""
    return _current_sdk == "opencode"


def set_api_config(
    api_key: str | None = None,
    auth_token: str | None = None,
    base_url: str | None = None,
) -> None:
    """Set custom API configuration for the SDK.

    These values will be used to override environment variables when making API calls.

    Args:
        api_key: Custom API key (ANTHROPIC_API_KEY)
        auth_token: Custom auth token (ANTHROPIC_AUTH_TOKEN)
        base_url: Custom base URL (ANTHROPIC_BASE_URL)
    """
    global _custom_api_key, _custom_auth_token, _custom_base_url
    _custom_api_key = api_key
    _custom_auth_token = auth_token
    _custom_base_url = base_url


def get_api_config() -> tuple[str | None, str | None, str | None]:
    """Get the current API configuration.

    Returns:
        Tuple of (api_key, auth_token, base_url)
    """
    return _custom_api_key, _custom_auth_token, _custom_base_url


def get_api_env_vars() -> dict[str, str]:
    """Get environment variables for API configuration.

    Returns a dictionary of environment variables that should be set
    for custom API configuration (MiniMax, etc.).
    """
    env_vars = {}

    # Check custom config first
    api_key, auth_token, base_url = get_api_config()

    if api_key:
        env_vars["ANTHROPIC_API_KEY"] = api_key
    if auth_token:
        env_vars["ANTHROPIC_AUTH_TOKEN"] = auth_token
    if base_url:
        env_vars["ANTHROPIC_BASE_URL"] = base_url

    # Also check environment variables
    for var in ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]:
        if var not in env_vars and os.environ.get(var):
            env_vars[var] = os.environ[var]

    return env_vars
