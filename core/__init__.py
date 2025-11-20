"""Core package exports for Transcript → Ad project."""
from .transcription import transcribe_text
from .analysis import analyze_transcript
from .ad_generator import generate_ad
from .gap_scanner import scan_gaps
from .storyboard import create_storyboard

# New modular interfaces and pipeline
from .asr import ASRInterface, LocalASR
from .nlg import NLGInterface, SimpleNLG
from .pipeline import run_pipeline

__all__ = [
    "transcribe_text",
    "analyze_transcript",
    "generate_ad",
    "scan_gaps",
    "create_storyboard",
    "ASRInterface",
    "LocalASR",
    "NLGInterface",
    "SimpleNLG",
    "run_pipeline",
]
