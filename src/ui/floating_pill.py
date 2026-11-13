"""Compatibilidade retroativa: redireciona para src.ui.components.pill_widget."""
from src.ui.components.pill_widget import FloatingPill
from src.ui.components.waveform import AudioWaveformWidget
__all__ = ["FloatingPill", "AudioWaveformWidget"]
