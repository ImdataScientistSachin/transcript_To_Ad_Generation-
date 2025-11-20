"""High-level pipeline orchestration.

This module wires ASR -> Analysis -> NLG -> Storyboard steps into a
single `run_pipeline` function. Backends are pluggable via the ASR/NLG
interfaces created in `core.asr` and `core.nlg`.
"""
from typing import Dict, Optional
import logging

from .asr import ASRInterface, LocalASR
from .nlg import NLGInterface, SimpleNLG
from .analysis import analyze_transcript
from .gap_scanner import scan_gaps
from .storyboard import create_storyboard

logger = logging.getLogger(__name__)


def run_pipeline(
    source,
    asr: Optional[ASRInterface] = None,
    nlg: Optional[NLGInterface] = None,
) -> Dict[str, object]:
    """Run the default transcript -> ad pipeline.

    Args:
        source: Raw input for ASR (text, bytes, or path depending on backend).
        asr: Optional ASR backend. If None, `LocalASR` will be used.
        nlg: Optional NLG backend. If None, `SimpleNLG` will be used.

    Returns:
        A dict with keys: `transcript`, `analysis`, `ad_copy`, `gaps`, `storyboard`.
    """
    if asr is None:
        asr = LocalASR()
    if nlg is None:
        nlg = SimpleNLG()

    transcript = asr.transcribe(source)
    analysis = analyze_transcript(transcript)
    ad_copy = nlg.generate(analysis)
    gaps = scan_gaps(transcript)
    storyboard = create_storyboard(analysis)
    result = {
        "transcript": transcript,
        "analysis": analysis,
        "ad_copy": ad_copy,
        "gaps": gaps,
        "storyboard": storyboard,
    }

    # Ensure the result contains only primitives (str, number, bool, None),
    # mappings, or sequences so downstream UI components (Streamlit) can
    # safely render them. Convert unknown objects (e.g., spaCy Doc/Span)
    # to their string representation.
    def _sanitize(value):
        # primitives
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        # mapping
        if isinstance(value, dict):
            return {str(k): _sanitize(v) for k, v in value.items()}
        # sequence
        if isinstance(value, (list, tuple, set)):
            return [_sanitize(v) for v in value]
        # spaCy types: try to preserve useful structure instead of opaque strings
        try:
            cls = value.__class__
            mod = cls.__module__
            if mod.startswith("spacy"):
                # Doc-like
                if hasattr(value, "ents"):
                    try:
                        ents = [
                            {"text": e.text, "label": getattr(e, "label_", str(getattr(e, 'label', '')))}
                            for e in value.ents
                        ]
                    except Exception:
                        ents = [str(e) for e in getattr(value, "ents", [])]
                    return {"text": str(value), "ents": ents}
                # Span or Token
                if hasattr(value, "text"):
                    out = {"text": str(value)}
                    if hasattr(value, "lemma_"):
                        out["lemma"] = getattr(value, "lemma_", None)
                    if hasattr(value, "pos_"):
                        out["pos"] = getattr(value, "pos_", None)
                    return out
        except Exception:
            # Log unexpected errors during spaCy-type sanitization and continue with string fallback
            logger.exception("Error while attempting to sanitize spaCy-like object")
        # fallback: convert to string
        try:
            return str(value)
        except Exception:
            return repr(value)

    sanitized = _sanitize(result)
    return sanitized
