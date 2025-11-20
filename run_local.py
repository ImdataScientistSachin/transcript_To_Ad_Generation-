"""Simple local runner to exercise the pipeline without Streamlit.

Usage:
    python run_local.py

This will call `core.run_pipeline` with a sample transcript and print
structured output to the console.
"""
from core import run_pipeline


SAMPLE = """
We launched our new product last quarter and customers love the simplicity.
It saves time and reduces cost.
Sign up today to get started.
"""


def main():
    # Run the main pipeline with a small inlined sample. This script is
    # intended for quick local experimentation without the Streamlit UI.
    result = run_pipeline(SAMPLE)
    print("=== AD COPY ===")
    print(result.get("ad_copy"))
    print("\n=== ANALYSIS ===")
    for k, v in result.get("analysis", {}).items():
        # Print concise keys and payloads to the console for developer review
        print(f"{k}: {v}")
    print("\n=== STORYBOARD ===")
    for i, f in enumerate(result.get("storyboard", []), 1):
        print(f"{i}. {f}")


if __name__ == "__main__":
    main()
