"""Ad generation utilities.

This module provides a small, deterministic `generate_ad` helper used as
a safe fallback when a more advanced LLM-based NLG is unavailable or
when JSON validation fails. The function is intentionally simple and
produces short ad copy appropriate for prototypes and tests.
"""
from typing import Dict, Any


def generate_ad(analysis: Dict[str, Any]) -> str:
    """Generate a short ad copy from analysis results.

    The function extracts a top keyword (if available) and a short
    highlight sentence to build a concise pitch + CTA. It aims to be
    conservative and deterministic so it can be used reliably in tests.

    Args:
        analysis: Output from `analyze_transcript`.

    Returns:
        A short ad copy string.
    """
    keywords = analysis.get("keywords", []) or []
    highlights = analysis.get("highlights", []) or []

    # Determine top term safely
    top_term = None
    if keywords:
        first = keywords[0]
        if isinstance(first, dict):
            top_term = first.get("term")
        else:
            top_term = first

    # Helper to filter out title/metadata-like lines
    def _is_title_like(s: str) -> bool:
        if not s:
            return True
        s_low = s.lower()
        markers = ["transcript", "source vibe", "motivational interview", "career pivot", "~", "(career pivot"]
        if any(m in s_low for m in markers):
            return True
        if len(s.split()) < 6:
            return True
        return False

    # Pick the best body sentence from highlights (prefer non-title-like)
    body = None
    for h in highlights:
        if not _is_title_like(h):
            body = h.strip()
            break
    if not body and highlights:
        body = highlights[0].strip()
    if not body:
        body = "Discover more today."

    # Truncate long bodies to keep ad concise
    max_len = 180
    if len(body) > max_len:
        body = body[: max_len - 3].rstrip() + "..."

    # Build lead text
    if top_term and isinstance(top_term, str) and len(top_term) >= 3:
        lead = f"Introducing {top_term.title()}"
    else:
        lead = "Introducing our new product"

    call_to_action = "Visit our site to learn more."
    return f"{lead} — {body} {call_to_action}"
