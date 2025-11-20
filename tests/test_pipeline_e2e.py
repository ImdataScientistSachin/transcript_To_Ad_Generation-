from core.pipeline import run_pipeline


def test_run_pipeline_e2e(monkeypatch):
    # Mock ASR LocalASR.transcribe to return fixed transcript
    def fake_transcribe(self, source):
        return {
            "text": "I love using product X. It's fast and reliable.",
            "duration_seconds": 30,
        }

    monkeypatch.setattr("core.pipeline.LocalASR.transcribe", fake_transcribe)

    # Mock LLM used by gap scanner and nlg
    def fake_safe_chat(messages, prefer_json=True, **kwargs):
        return {
            "hooks": "Try: 'Shave seconds off your workflow.'",
            "social_proof": "Add: 'Used by thousands'",
            "urgency": "Add: 'Limited stock'",
            "emotional_appeal": "Make it aspirational",
            "sustainability": "Add eco note",
        }

    monkeypatch.setattr("core.llm.safe_chat_completion", fake_safe_chat)

    res = run_pipeline("dummy source")
    assert "transcript" in res and "analysis" in res and "ad_copy" in res
    # gaps should be a dict with the expected keys
    gaps = res.get("gaps")
    assert isinstance(gaps, dict)
    for k in ("hooks", "social_proof", "urgency", "emotional_appeal", "sustainability"):
        assert k in gaps
