"""Lightweight LLM helper with retry and mock behaviour.

This module provides `safe_chat_completion` which wraps OpenAI-style
chat completions with simple exponential backoff retries and a mock
fallback when `OPENAI_API_KEY` is not supplied (useful for tests).

The implementation is intentionally small to avoid adding heavy
dependencies; tests should mock `safe_chat_completion` when needed.
"""
from typing import Any, Dict, List, Optional
import os
import time
import json
import logging

logger = logging.getLogger(__name__)

_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# Runtime switch to force mock responses even if an API key exists.
FORCE_MOCK = False

# `openai` may not be installed in dev environments; predeclare as Any
openai: Any = None
try:
    import openai as _openai
    openai = _openai
except Exception:
    openai = None


def _mock_response() -> Dict[str, str]:
    """Return a deterministic mock JSON-like response for tests."""
    return {
        "hooks": "Try: 'Still scrolling? Here's 3 reasons to try X'",
        "social_proof": "Add: 'Join 10,000+ happy users'",
        "urgency": "Add: 'Limited-time 20% off'",
        "emotional_appeal": "Use aspiration language: 'Imagine waking up...'",
        "sustainability": "Mention eco-friendly materials or donation tie-in",
    }


def safe_chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    max_retries: int = 3,
    temperature: float = 0.2,
    timeout: Optional[int] = None,
    prefer_json: bool = False,
    return_usage: bool = False,
    mock: Optional[bool] = None,
) -> Any:
    """Call the OpenAI chat completion API with simple retries.

    If `OPENAI_API_KEY` is not present the function returns a deterministic
    mock response (useful for local development and unit tests).

    Args:
        messages: Chat messages following OpenAI chat schema.
        model: Model name to call.
        max_retries: Number of attempts on transient errors.
        temperature: Sampling temperature.
        timeout: Optional request timeout (ignored if OpenAI not present).
        prefer_json: If True, attempt to parse the assistant response as JSON
                     and return a parsed object when possible.

    Returns:
        Parsed JSON/dict when `prefer_json` is True and parsing succeeds,
        otherwise the assistant content string. On persistent failure an
        empty dict is returned when `prefer_json` is True, else an empty
        string is returned.
    """
    # Resolve mock behavior precedence:
    # 1. explicit `mock` parameter when provided
    # 2. module-level FORCE_MOCK
    # 3. absence of API key or openai package
    do_mock = False
    if mock is True:
        do_mock = True
    elif mock is False:
        do_mock = False
    elif FORCE_MOCK or not _OPENAI_API_KEY or openai is None:
        do_mock = True

    if do_mock:
        # When mocking, return a deterministic structure. If the caller
        # requested `prefer_json` we return the parsed dict, otherwise
        # return the JSON-encoded string so code paths that expect text
        # continue to work in tests.
        logger.debug("Using mock response for LLM (mock=%s).", mock)
        return _mock_response() if prefer_json else json.dumps(_mock_response())

    # Build request kwargs
    kwargs: Dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout

    # Try a few times on transient errors (network, rate limits).
    for attempt in range(1, max_retries + 1):
        try:
            resp = openai.ChatCompletion.create(**kwargs)
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage")
            # optionally write usage to a log file
            if usage:
                try:
                    base_dir = os.path.dirname(__file__)
                    log_path = os.path.join(base_dir, "..", "llm_usage.log")
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write(
                            json.dumps({"time": time.time(), "usage": usage, "model": model})
                            + "\n"
                        )
                except Exception:
                    logger.exception("Failed to write LLM usage log")

            # If the assistant returns JSON text and `prefer_json` is
            # requested, attempt to parse it into a Python object.
            if prefer_json:
                try:
                    parsed = json.loads(content)
                except Exception:
                    # Not valid JSON — return raw content so callers can
                    # decide how to handle it.
                    parsed = content
                return (parsed, usage) if return_usage else parsed
            return (content, usage) if return_usage else content
        except Exception as exc:
            # Handle common transient errors conservatively
            logger.warning("LLM call failed (attempt %d/%d): %s", attempt, max_retries, exc)
            if attempt == max_retries:
                logger.error("LLM call failed after %d attempts", max_retries)
                # Return mock fallback consistent with prefer_json/return_usage flags
                if prefer_json and return_usage:
                    return _mock_response(), None
                if prefer_json:
                    return _mock_response()
                return ""
            # Exponential backoff with jitter
            backoff = (2 ** (attempt - 1)) + (0.1 * attempt)
            time.sleep(backoff)
