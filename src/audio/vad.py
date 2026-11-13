"""
Detector de Atividade de Voz (VAD - Voice Activity Detection).
Requer energia vocal sustentada para rejeitar estalos de digitação e latidos esporádicos.
"""

import time
import numpy as np


class VoiceActivityDetector:
    """Classifica blocos de áudio em fala sustentada versus silêncio/ruído transitório."""

    def __init__(self, silence_threshold: float = 0.016, silence_duration: float = 0.9, min_sustained_frames: int = 5):
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_sustained_frames = min_sustained_frames

        self._sustained_frames = 0
        self._voice_active = False
        self._last_speech_time = 0.0
        self._start_time = 0.0

    def reset(self):
        """Reinicia os contadores de detecção."""
        self._sustained_frames = 0
        self._voice_active = False
        self._last_speech_time = time.time()
        self._start_time = time.time()

    @staticmethod
    def calculate_rms(audio_block: np.ndarray) -> float:
        """Calcula a energia RMS (Root Mean Square) do bloco de áudio."""
        if audio_block.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio_block ** 2)))

    def process_block(self, rms_energy: float) -> tuple[bool, bool]:
        """
        Processa a energia RMS de um bloco.
        Retorna: (is_voice_active, should_trigger_auto_stop)
        """
        now = time.time()

        if rms_energy >= self.silence_threshold:
            self._sustained_frames += 1
            if self._sustained_frames >= self.min_sustained_frames:
                self._voice_active = True
                self._last_speech_time = now
        else:
            self._sustained_frames = max(0, self._sustained_frames - 1)

            if self._voice_active:
                pause_duration = now - self._last_speech_time
                total_duration = now - self._start_time
                if pause_duration >= self.silence_duration and total_duration >= 0.5:
                    self._voice_active = False
                    return False, True

        return self._voice_active, False
