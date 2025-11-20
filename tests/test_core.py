import os
import sys

# Ensure the package root (one level up) is on sys.path so tests can import `core`.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import core  # noqa: E402


def test_dummy_analysis():
    text = "This is a short transcript about our great product and value."
    transcript = core.transcribe_text(text)
    analysis = core.analyze_transcript(transcript)
    assert isinstance(analysis, dict)
    assert "keywords" in analysis
    assert isinstance(analysis["keywords"], list)
    # For non-empty input we expect at least one keyword (heuristic or spaCy)
    assert len(analysis["keywords"]) >= 1
    # Each keyword item should be a dict with term and score
    kw = analysis["keywords"][0]
    assert isinstance(kw, dict)
    assert "term" in kw and "score" in kw
