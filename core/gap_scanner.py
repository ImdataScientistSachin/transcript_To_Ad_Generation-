"""Creative gap scanner.

This implementation uses a lightweight LLM wrapper (`core.llm.safe_chat_completion`)
to produce a structured JSON object describing creative gaps and suggestions.
The function accepts either a `transcript` dict (with a `text` field) or an
`analysis` dict (as produced by `core.analysis.analyze_transcript`). It
returns a mapping with keys: `hooks`, `social_proof`, `urgency`,
`emotional_appeal`, `sustainability`.
"""
from typing import Any, Dict
import json
import logging
from .llm import safe_chat_completion

logger = logging.getLogger(__name__)


def _build_prompt(text: str) -> str:
    return (
        "You are an expert ad analyst. Given the transcript or analysis below, "
        "identify creative gaps and suggest concise improvements. Respond ONLY in JSON with keys: "
        "\"hooks\", \"social_proof\", \"urgency\", \"emotional_appeal\", \"sustainability\". "
        "Each value should be a short string with a suggested change or an empty string if none.\n\n"
        "Input:\n" + text
    )


def scan_gaps(transcript_or_analysis: Dict[str, Any]) -> Dict[str, str]:
    """Return structured gap suggestions for an input transcript or analysis.

    Args:
        transcript_or_analysis: dict containing either `text` (transcript) or
            `highlights`/`keywords` (analysis output).

    Returns:
        Dict with keys: `hooks`, `social_proof`, `urgency`, `emotional_appeal`,
        `sustainability`. Values are strings (possibly empty).
    """
    # Attempt to extract usable text for the LLM prompt
    text = ""
    if not transcript_or_analysis:
        return {k: "" for k in ("hooks", "social_proof", "urgency", "emotional_appeal", "sustainability")}

    if isinstance(transcript_or_analysis, dict):
        # Prefer full transcript text if present
        text = transcript_or_analysis.get("text") or ""
        # Fallback to joined highlights or keywords from analysis
        if not text:
            highlights = transcript_or_analysis.get("highlights") or []
            if isinstance(highlights, (list, tuple)) and highlights:
                text = "\n".join(highlights)
            else:
                kws = transcript_or_analysis.get("keywords") or []
                if isinstance(kws, (list, tuple)) and kws:
                    # keywords may be dicts with 'term'
                    terms = [k.get("term") if isinstance(k, dict) else str(k) for k in kws[:10]]
                    text = ", ".join([t for t in terms if t])

    prompt = _build_prompt(text)
    messages = [
        {"role": "system", "content": "You are a helpful and concise ad analyst."},
        {"role": "user", "content": prompt},
    ]

    resp = safe_chat_completion(messages, prefer_json=True)

    # Normalize response to dict with required keys
    keys = ("hooks", "social_proof", "urgency", "emotional_appeal", "sustainability")
    out: Dict[str, str] = {k: "" for k in keys}

    if isinstance(resp, dict):
        for k in keys:
            v = resp.get(k)
            if isinstance(v, str):
                out[k] = v.strip()
            elif v is not None:
                out[k] = str(v)
    else:
        # resp might be a JSON string — attempt to parse it. If parsing
        # fails, leave the default empty suggestions; callers should treat
        # empty strings as "no suggestion" rather than a hard failure.
        try:
            parsed = json.loads(resp)
            for k in keys:
                v = parsed.get(k)
                if isinstance(v, str):
                    out[k] = v.strip()
                elif v is not None:
                    out[k] = str(v)
        except Exception as e:
            # Keep defaults and log the incident for debugging.
            logger.debug("Gap scanner returned non-JSON output: %s", e)

    return out
