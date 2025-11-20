from core.gap_scanner import scan_gaps


def test_scan_gaps_with_mock(monkeypatch):
    """Test that `scan_gaps` returns the expected keys when the LLM is mocked."""

    def fake_safe_chat(messages, prefer_json=True, **kwargs):
        return {
            "hooks": "Try: 'Still scrolling? Here's 3 reasons to try X'",
            "social_proof": "Add: 'Join 10,000+ happy users'",
            "urgency": "Add: 'Limited-time 20% off'",
            "emotional_appeal": "Use aspiration language: 'Imagine waking up...'",
            "sustainability": "Mention eco-friendly materials or donation tie-in",
        }

    # Patch the llm helper used by gap_scanner
    monkeypatch.setattr("core.llm.safe_chat_completion", fake_safe_chat)

    transcript = {"text": "This product saved me time and money.", "duration_seconds": 30}
    gaps = scan_gaps(transcript)

    assert isinstance(gaps, dict)
    # Ensure keys are present and non-empty
    for key in ("hooks", "social_proof", "urgency", "emotional_appeal", "sustainability"):
        assert key in gaps
        assert gaps[key] != ""
