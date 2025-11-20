"""Simple transcription helpers.

This module provides a thin wrapper for transcript input. In a full app
this would contain code to call a speech-to-text model or to parse speaker
labels. For the scaffold it returns the provided text as the "transcript".
"""
from typing import Dict, Any


def transcribe_text(text: str) -> Dict[str, Any]:
    """Return a minimal transcript structure for downstream processing.

    Args:
        text: Raw transcript text.

    Returns:
        A dict containing the transcript text and a simple metadata placeholder.
    """
    return {"text": text, "language": "en", "duration_seconds": None}
