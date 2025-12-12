# 🎬 Transcript-to-Ad Generator

> **Transform spoken content into high-converting video ads in seconds.**

A sophisticated AI-driven pipeline that ingests audio/video transcripts, analyzes them using NLP, and automatically generates ready-to-use video ad scripts, storyboards, and previews.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Status](https://img.shields.io/badge/status-active-success)

---

## ✨ Features

-   **Deep Content Analysis**: Uses NLP (spaCy) to extract keywords, named entities, and key highlights from transcripts.
-   **Intelligent Ad Generation**: 
    -   **LLM Mode**: Uses structured prompting to create professional ad copy with compelling CTAs.
    -   **Simple Mode**: Deterministic rule-based generation for fast local testing.
-   **Visual Storyboarding**: Automatically maps ad copy to visual frames.
-   **Video Previews**: Renders MP4 video previews on-the-fly using **MoviePy**.
-   **Interactive UI**: A polished **Streamlit** interface with premium aesthetics, dark mode, and real-time feedback.
-   **Background Processing**: Supports asynchronous rendering via Redis Queue (RQ) for heavy workloads.
-   **Smart Caching**: Built-in system for caching expensive API calls and rendering steps.
-   **Production Ready**: Dockerized and includes robust logging and error handling.

## 🛠️ Technology Stack

-   **Frontend**: Streamlit (Custom CSS for premium UI)
-   **Core Logic**: Python 3.9+
-   **NLP**: spaCy, TextBlob
-   **Video Processing**: MoviePy, Pillow
-   **Async Workers**: Redis, RQ (Redis Queue)
-   **Containerization**: Docker & Docker Compose
-   **Quality**: pytest, flake8, mypy, pre-commit

## 🚀 Getting Started

### Prerequisites

-   Python 3.9+
-   [FFmpeg](https://ffmpeg.org/) (required for local video rendering)
-   Docker (optional, for containerized execution)

### 📦 Quick Start (Local)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/transcript-to-ad.git
    cd transcript-to-ad
    ```

2.  **Set up environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

5.  Open `http://localhost:8501` in your browser.

### 🐳 Run with Docker (Recommended)

Easily spin up the entire stack including the Redis worker:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`.

## 📂 Project Structure

```
transcript-to-ad/
├── core/                   # Business Logic & Pipeline
│   ├── analysis.py         # NLP & Text Analysis
│   ├── ad_generator.py     # Ad Copy Generation Logic
│   ├── video.py            # Video Rendering (MoviePy)
│   ├── pipeline.py         # Main Orchestration
│   ├── gap_scanner.py      # Opportunity Detection
│   ├── llm.py              # LLM Integration
│   ├── nlg.py              # Natural Language Generation
│   └── queue.py            # Redis Queue Interface
├── scripts/                # Utility Scripts (Worker, Redis helpers)
├── tests/                  # Unit & Integration Tests
├── app.py                  # Main Streamlit Application
├── run_local.py            # CLI Runner for Pipeline
├── Dockerfile              # App Container Config
├── Dockerfile.worker       # Worker Container Config
└── requirements.txt        # Python Dependencies
```

## 🧪 Testing & Quality

Run the test suite to ensure everything is working correctly:

```bash
# Run unit tests
pytest tests/

# Run type checks
mypy core/

# Run linter
flake8 core/
```

## ⌨️ CLI Usage

You can also run the pipeline directly from the command line without the UI:

```bash
python run_local.py
```

This will process a sample transcript and print the detailed analysis and ad copy to the console.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

*Generated for the Transcript-to-Ad Project.*
