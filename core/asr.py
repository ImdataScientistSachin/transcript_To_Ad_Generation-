"""ASR interface and a simple local implementation.

Defines an abstract-like interface for automatic speech recognition (ASR)
implementations so the rest of the code can depend on an interface and
receive different backends via dependency injection.
"""
from typing import Dict


class ASRInterface:
    """A minimal ASR interface.

    Implementations should provide `transcribe` that accepts either raw
    bytes/audio path or plain text (for testing) and returns a transcript
    dict compatible with `core.transcription.transcribe_text`.
    """

    def transcribe(self, source) -> Dict[str, object]:
        raise NotImplementedError()


class LocalASR(ASRInterface):
    """Simple local ASR shim that treats input as pre-transcribed text.

    This is useful for testing and local runs without a real ASR model.
    """

    def transcribe(self, source) -> Dict[str, object]:
        # If `source` is already a dict-like transcript, pass through
        if isinstance(source, dict) and "text" in source:
            return source
        # If it's bytes (e.g., uploaded file), decode as UTF-8 text
        if isinstance(source, (bytes, bytearray)):
            text = source.decode("utf-8")
        else:
            text = str(source)
        # Minimal transcript shape
        return {"text": text, "language": "en", "duration_seconds": None}
