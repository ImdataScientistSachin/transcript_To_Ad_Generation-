"""Create a simple storyboard for ad frames from analysis output."""
from typing import Dict, List, Any


def create_storyboard(analysis: Dict[str, Any]) -> List[str]:
    """Return a list of short frame descriptions for a storyboard.

    Args:
        analysis: Output from `analyze_transcript`.

    Returns:
        A list of strings describing frames.
    """
    keywords = analysis.get("keywords", []) or []
    highlights = analysis.get("highlights", []) or []

    # Frames are human-readable short descriptions meant for rapid prototyping
    # of an ad storyboard. Keep them short — they will be converted to simple
    # preview slides or used as guidance for visual asset selection.
    frames = []
    top = None
    if keywords:
        if isinstance(keywords[0], dict):
            top = keywords[0].get("term")
        else:
            top = keywords[0]
    if top:
        frames.append(f"Introduce: {top.title()} — what it does")
    # Prefer a short highlight (best sentence) for the customer quote
    if highlights and highlights[0]:
        quote = highlights[0].strip()
        # Truncate long quotes for frames
        if len(quote) > 140:
            quote = quote[:137].rstrip() + "..."
        frames.append(f"Customer says: \"{quote}\"")
    frames.append("Call-to-action: Visit website / Sign up")
    return frames
