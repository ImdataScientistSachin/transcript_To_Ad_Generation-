<div align="center">

# 🎬 Transcript-to-Ad Generator

### NLP · Generative AI · Video Rendering · Async Processing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/ImdataScientistSachin/Transcript-to-Ad-Generator/actions)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](https://github.com/ImdataScientistSachin/Transcript-to-Ad-Generator)

[![Python](https://img.shields.io/badge/Python_3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=flat&logo=spacy&logoColor=white)](https://spacy.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat)](https://ollama.ai/)

> **Transform spoken content into high-converting video ads — in seconds.**
>
> An AI-driven pipeline that ingests audio/video transcripts, analyses them with NLP, and automatically generates ad scripts, storyboards, and MP4 video previews.

[**⚙️ CI/CD**](https://github.com/ImdataScientistSachin/Transcript-to-Ad-Generator/actions) · [**📂 Structure**](#️-project-structure) · [**🚀 Quick Start**](#-quick-start) · [**👤 Author**](#-author)

</div>

---

## 📖 Overview

**Transcript-to-Ad Generator** is a production-ready, end-to-end pipeline for converting raw transcripts into polished advertising content. It combines **spaCy NLP** for intelligent content extraction, **Ollama (local LLM)** for creative ad-copy generation via structured prompting, **MoviePy** for on-the-fly video rendering, and **Redis Queue** for asynchronous background processing — all wrapped in a premium **Streamlit** UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Deep NLP Analysis** | spaCy + TextBlob extract keywords, named entities, sentiment, and highlights |
| ✍️ **Dual-Mode Ad Generation** | **Ollama LLM mode** for creative copy · **Simple mode** for fast deterministic output |
| 🎞️ **Visual Storyboarding** | Auto-maps ad copy to visual frames with scene descriptions |
| 🎬 **Video Preview Rendering** | Generates MP4 previews on-the-fly via MoviePy |
| ⚡ **Async Background Jobs** | Redis Queue (RQ) workers handle heavy rendering without blocking the UI |
| 🖥️ **Premium Web UI** | Dark-mode Streamlit interface with custom CSS and real-time feedback |
| 💾 **Smart Caching** | Caches expensive LLM and rendering calls for speed |
| 🐳 **Production Ready** | Fully Dockerized with multi-container compose, pre-commit hooks, and structured logging |

---

## 🤖 Ollama Integration — Local LLM Prompt Generation

This project uses **Ollama** to run large language models locally — no API key, no cost, no data leaving your machine. The `core/llm.py` module handles structured prompt construction and response parsing.

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model (Mistral recommended)
ollama pull mistral

# 3. Start the Ollama server
ollama serve
```

Once running, the pipeline connects to `http://localhost:11434`. Switch models by setting `OLLAMA_MODEL` in your `.env` file.

---

## 🧬 Tech Stack

| Layer | Technology |
|---|---|
| **NLP** | spaCy · TextBlob |
| **LLM / Prompt Generation** | Ollama (local) — Mistral / Llama 3 |
| **Video Rendering** | MoviePy · Pillow · FFmpeg |
| **Async Workers** | Redis · RQ (Redis Queue) |
| **Web UI** | Streamlit (custom CSS, dark mode) |
| **Backend** | Python 3.9+ |
| **Containerisation** | Docker · Docker Compose |
| **Quality & CI** | pytest · flake8 · mypy · pre-commit · GitHub Actions |

---

## 🏗️ Project Structure

```text
Transcript-to-Ad-Generator/
├── .github/workflows/          # CI/CD — GitHub Actions pipelines
├── core/
│   ├── analysis.py             # NLP & text analysis (spaCy, TextBlob)
│   ├── ad_generator.py         # Ad copy generation logic
│   ├── llm.py                  # Ollama LLM integration & prompt generation
│   ├── nlg.py                  # Natural language generation helpers
│   ├── video.py                # Video rendering (MoviePy)
│   ├── pipeline.py             # Main orchestration layer
│   ├── gap_scanner.py          # Opportunity & gap detection
│   └── queue.py                # Redis Queue interface
├── scripts/                    # Worker & Redis utility scripts
├── tests/                      # Unit & integration tests (pytest)
├── app.py                      # Streamlit web application
├── run_local.py                # CLI runner for the pipeline
├── utils_logging.py            # Structured logging setup
├── Dockerfile                  # App container
├── Dockerfile.worker           # RQ worker container
├── docker-compose.yml          # Full stack compose (app + worker + Redis)
├── Makefile                    # Dev shortcuts
├── pyproject.toml              # Project metadata & tool config
├── mypy.ini                    # Type checking config
├── .flake8                     # Linting config
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .env.example                # Environment variable template
└── requirements.txt            # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) — required for local video rendering
- [Ollama](https://ollama.ai/) — for LLM-powered ad generation
- Docker — optional, recommended for full stack

### 1 · Clone & Install

```bash
git clone https://github.com/ImdataScientistSachin/Transcript-to-Ad-Generator
cd Transcript-to-Ad-Generator

python -m venv .venv
# Windows
.\.venv\Scripts\Activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2 · Configure Environment

```bash
cp .env.example .env
# Edit .env — set OLLAMA_MODEL, Redis connection, etc.
```

### 3 · Launch the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🐳 Docker — Full Stack (Recommended)

Spin up the app, Redis, and the background worker in a single command:

```bash
docker-compose up --build
```

| Service | Port | Description |
|---|---|---|
| Streamlit App | `8501` | Main web interface |
| Redis | `6379` | Job queue backend |
| RQ Worker | — | Background video renderer |

---

## 🧪 Testing & Code Quality

```bash
# Run the full test suite
pytest tests/

# Type checking
mypy core/

# Linting
flake8 core/

# Run all pre-commit hooks manually
pre-commit run --all-files
```

> CI/CD via **GitHub Actions** runs linting, type checks, and tests automatically on every push.

---

## ⌨️ CLI Usage

Run the full pipeline directly from the command line without the UI:

```bash
python run_local.py
```

Processes a sample transcript and prints the NLP analysis and generated ad copy to the console — useful for scripting and batch workflows.

---

## 📋 Full Audit Status

| Item | Status | Notes |
|---|---|---|
| GitHub Actions CI/CD | ✅ Done | `.github/workflows/` confirmed present |
| Ollama LLM Integration | ✅ Done | `core/llm.py` — local prompt generation |
| Docker + Compose | ✅ Done | App + worker + Redis fully composed |
| Redis Queue workers | ✅ Done | `Dockerfile.worker` + `core/queue.py` |
| Code quality tooling | ✅ Done | flake8, mypy, pre-commit all configured |
| README quality | ✅ Done | This document |
| Repo name (trailing dash) | ❌ Pending | Original name `transcript_To_Ad_Generation-` — rename in GitHub Settings |
| GitHub About description | ❌ Pending | No sidebar description set — add via ⚙️ repo Settings |
| Topics | ⚠️ Partial | Add: `ollama` `github-actions` `moviepy` — verify `generative-ai` is present |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch — `git checkout -b feature/your-feature`
3. Commit your changes — `git commit -m 'Add your feature'`
4. Push to the branch — `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License** — free to use, modify, and distribute.
See [`LICENSE`](./LICENSE) for details.

---

## 👤 Author

**Sachin Paunikar**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sachin-paunikar-datascientists)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/ImdataScientistSachin)

---

<div align="center">
<sub>Built with ❤️ · Powered by spaCy · Ollama · MoviePy · Redis · Streamlit</sub>
</div>
