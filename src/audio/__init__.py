"""
Pacote de captura e processamento acústico de áudio.
"""
from src.audio.filters import AcousticFilter
from src.audio.vad import VoiceActivityDetector
from src.audio.recorder import AudioRecorder

__all__ = ["AcousticFilter", "VoiceActivityDetector", "AudioRecorder"]
