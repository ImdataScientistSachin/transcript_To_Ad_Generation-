import os
import sys

# Ensure the package root (one level up) is on sys.path so tests can import `core`.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import run_pipeline  # noqa: E402


def test_run_pipeline_basic():
    src = "This is a test transcript about an amazing product that helps users."
    result = run_pipeline(src)
    assert "analysis" in result
    assert "ad_copy" in result
    assert isinstance(result["ad_copy"], str)
    # analysis should contain a non-empty keywords list
    assert isinstance(result["analysis"].get("keywords"), list)
    assert len(result["analysis"].get("keywords")) >= 1
    kw = result["analysis"].get("keywords")[0]
    assert isinstance(kw, dict)
    assert "term" in kw and "score" in kw
