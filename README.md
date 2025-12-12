# Transcript → Ad

[![CI](https://github.com/your-org/transcript_To_Ad/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/transcript_To_Ad/actions)

A small scaffold for converting spoken transcripts into short ad copy,
storyboards and simple insights. This project provides minimal starter
implementations so you can plug in real models (ASR, NLP, NLG) later.

Quickstart
 Open a terminal and change to the project folder:

```powershell
```powershell
cd transcript_To_Ad
```


```powershell
```powershell
streamlit run app.py
```

Project layout

- `app.py` — Streamlit UI.
- `core/` — core modules: transcription, analysis, ad generation, gap scanning, storyboard.
- `tests/` — basic pytest tests.

Next steps

- Replace placeholder functions with real ASR and NLP model calls.

Next steps

- Replace placeholder functions with real ASR and NLP model calls.
- Add CI and more comprehensive tests.

## Running Redis + Worker for local development

The project supports an asynchronous rendering path using RQ (Redis Queue). To exercise the full RQ worker flow locally you can start a Redis instance and then run the local worker.

I included a `docker-compose.yml` that starts Redis and a small PowerShell helper script to bring up Redis and run the worker.

From PowerShell run:

```powershell
.\scripts\start_dev_redis.ps1
```

This will:
- start a Redis container (via `docker compose` or `docker-compose`),
- wait until `localhost:6379` is reachable (timeout defaults to 30s),
- then run the local worker `python scripts/worker.py` in your console so you can see worker logs.

If you prefer to manage Redis manually with Docker, you can run:

```powershell
# transcript_To_Ad — Transcript → Short Ad Prototype

Lightweight prototype that converts meeting/transcript text into short ad concepts, storyboards and preview renders. Built as a developer-first demo for iterative experimentation with LLMs, local video preview rendering, and an asynchronous queue worker for background jobs.

Badges
- Build / Tests: [![tests](https://github.com/your-org/transcript_To_Ad/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/transcript_To_Ad/actions)

Elevator Pitch
----------------
This repository demonstrates a compact pipeline that turns spoken transcripts into short, structured ad concepts using a mix of analysis heuristics and LLM-powered natural language generation. It includes:

- A safe LLM wrapper with retry, mock mode and usage logging.
- A creative gap scanner that surfaces emotional hooks, urgency, social proof and sustainability angles.
- An LLM-backed NLG engine that returns validated ad JSON and falls back to a simple generator when validation fails.
- File-backed caching to reduce LLM calls during iteration.
- Storyboard creation and a small preview renderer (Pillow + MoviePy) with an optional Redis/RQ worker for async rendering.
- Streamlit UI for interactive experimentation.

Why this repo is interesting for recruiters
------------------------------------------
- Shows end-to-end product thinking: ASR/analysis → creative gap detection → NLG → storyboard → preview rendering.
- Demonstrates pragmatic engineering trade-offs: local-first design, graceful fallbacks, and containerized worker orchestration.
- Includes tests, CI, and developer convenience scripts to spin up Redis/worker locally.

Quick Features
--------------
- `core/llm.py`: safe LLM wrapper with optional mock responses and usage logging.
- `core/gap_scanner.py`: LLM-assisted creative gap detection.
- `core/nlg.py`: `LLMNLG` (LLM-backed) + `SimpleNLG` fallback and schema validation.
- `core/cache.py`: file-backed TTL cache to avoid repeated LLM calls.
- `core/video.py`: render storyboard previews (Pillow for raster text + MoviePy for composition).
- `core/queue.py` + `scripts/worker.py`: optional RQ/Redis queue and worker for background renders.
- `app.py`: Streamlit UI to upload/paste transcripts, run pipeline and preview/download renders.

Quickstart (Developer)
----------------------
Prerequisites

- Python 3.10+ (3.11 recommended).
- Optional: Docker & Docker Compose for running Redis and the containerized worker.

Install dependencies (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install developer tooling (optional but recommended)
--------------------------------------------------

Install `pre-commit` and register the git hooks so contributors run linters and mypy locally before committing:

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files    # optional: run checks now across the repo
```

Run tests:

```powershell
python -m pytest -q
```

Run the Streamlit app (from project root):

```powershell
python -m streamlit run app.py
```

Local async worker (optional)

Start Redis (local Docker):

```powershell
docker compose up -d redis
```

Start the Python worker (in a separate terminal):

```powershell
python scripts/worker.py
```

Or start both Redis + worker via Docker Compose (requires Docker):

```powershell
docker compose up -d
```

Notes

- The Streamlit UI includes a thread-based fallback renderer when Redis is not available — you can iterate without Docker.
- Configure LLM credentials via `OPENAI_API_KEY` (if using OpenAI). The code has a deterministic `mock` mode useful for tests and demos.

Development Workflow
--------------------
1. Run tests: `python -m pytest`
2. Run the app and exercise the UI: `python -m streamlit run app.py`
3. For full async rendering, start Redis and `scripts/worker.py` or use Docker Compose.

Architecture (High Level)
-------------------------

Transcript → ASR (optional) → Analysis → Gap Scanner (LLM) → NLG (LLM-backed or simple) → Storyboard → Render (local or queue)

- Streamlit UI orchestrates the pipeline and provides a preview + download flow.
- `core/llm.py` centralizes LLM access and usage logging to `llm_usage.log`.
- `core/cache.py` reduces repeated LLM calls while iterating on prompts.

Where to look in the code
-------------------------
- Pipeline orchestration: `core/pipeline.py`
- LLM wrapper: `core/llm.py`
- Gap scanner: `core/gap_scanner.py`
- NLG backends: `core/nlg.py`
- Storyboard + rendering: `core/storyboard.py`, `core/video.py`
- Queue & worker: `core/queue.py`, `scripts/worker.py`
- App UI: `app.py`

Contributing / Next Steps
-------------------------
- Add linting and mypy checks to CI. (Planned: `requirements-dev.txt` + CI workflow changes.)
- Improve preview fidelity, transitions and low-memory rendering.
- Add persistent storage for assets (S3) and token-level cost reporting.

License & Contact
-----------------
This prototype is provided as-is for demonstration and hiring evaluation.
For questions or to run a live demo, contact the project owner.
