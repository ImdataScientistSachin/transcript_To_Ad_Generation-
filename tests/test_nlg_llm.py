from core.nlg import LLMNLG


def test_llm_nlg_generates_and_caches(monkeypatch, tmp_path):
    calls = {}

    def fake_safe_chat(messages, prefer_json=True, **kwargs):
        calls['called'] = True
        return {
            "hooks": "Hook: 'Stop scrolling. Try this now'",
            "segments": [
                {"start": 0.0, "end": 3.0, "text": "Hook line", "visual_cue": "closeup"},
                {"start": 3.0, "end": 12.0, "text": "Main message", "visual_cue": "product_shot"},
            ],
            "cta": "Buy now",
            "length_seconds": 15,
        }

    monkeypatch.setattr("core.nlg.safe_chat_completion", fake_safe_chat)

    analysis = {"keywords": [{"term": "speed", "score": 1.0}], "highlights": ["It saved me time"]}
    nlg = LLMNLG()
    out = nlg.generate(analysis)

    assert isinstance(out, dict)
    assert out.get("hooks")
    assert "segments" in out and isinstance(out["segments"], list)

    # second call should hit cache (no new call to safe_chat)
    calls.clear()
    out2 = nlg.generate(analysis)
    # safe_chat was not called again since we returned cached result
    assert calls == {}
    assert out2 == out
