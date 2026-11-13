"""
Sinais Qt para comunicação assíncrona entre threads e a interface visual.
"""

from PySide6.QtCore import QObject, Signal


class ControllerSignals(QObject):
    recording_started = Signal(str)      # modo: "direct" | "smart"
    amplitude_updated = Signal(float)    # volume RMS: 0.0 - 1.0
    transcribing_started = Signal()
    polishing_started = Signal()
    finished = Signal(str)               # texto final processado
    cancel = Signal()
    waiting_state = Signal()
