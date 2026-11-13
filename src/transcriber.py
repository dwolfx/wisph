"""Compatibilidade retroativa: redireciona para src.speech.transcriber."""
from src.speech.transcriber import WhisperTranscriber
__all__ = ["WhisperTranscriber"]
