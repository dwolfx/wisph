"""
Módulo de gravação de áudio via microfone.
Coordena captura de hardware sounddevice, filtragem acústica e disparo de VAD.
"""

import io
import threading
import numpy as np
import sounddevice as sd

from src.audio.filters import AcousticFilter
from src.audio.vad import VoiceActivityDetector
from src.config.settings import (
    SAMPLE_RATE,
    AUDIO_BLOCK_SECONDS,
    LOW_CUT_FREQUENCY_HZ,
    SILENCE_THRESHOLD_RMS,
    SILENCE_DURATION_SECONDS,
    MIN_SUSTAINED_VOICE_FRAMES
)


class AudioRecorder:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.filter = AcousticFilter(sample_rate=self.sample_rate, cutoff_hz=LOW_CUT_FREQUENCY_HZ)
        self.vad = VoiceActivityDetector(
            silence_threshold=SILENCE_THRESHOLD_RMS,
            silence_duration=SILENCE_DURATION_SECONDS,
            min_sustained_frames=MIN_SUSTAINED_VOICE_FRAMES
        )

        self.is_recording = False
        self.audio_frames = []
        self.stream = None
        self._lock = threading.Lock()

        self.amplitude_callback = None
        self.silence_callback = None

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return

        audio_data = indata.copy()
        with self._lock:
            self.audio_frames.append(audio_data)

        mono = np.mean(audio_data, axis=1) if audio_data.ndim > 1 else audio_data.flatten()
        filtered = self.filter.apply(mono)
        rms = self.vad.calculate_rms(filtered)

        level = min(1.0, rms * 12.0)
        if self.amplitude_callback:
            try:
                self.amplitude_callback(level)
            except Exception:
                pass

        _, should_stop = self.vad.process_block(rms)
        if should_stop and self.silence_callback and self.is_recording:
            cb = self.silence_callback
            self.silence_callback = None
            threading.Thread(target=cb, daemon=True).start()

    def start_recording(self, device=None, amplitude_callback=None, silence_callback=None):
        """Inicia a captura de áudio."""
        if self.is_recording:
            return

        self.amplitude_callback = amplitude_callback
        self.silence_callback = silence_callback
        self.filter.reset()
        self.vad.reset()

        with self._lock:
            self.audio_frames = []
            self.is_recording = True

        dev_info = sd.query_devices(device or sd.default.device[0])
        max_channels = int(dev_info.get("max_input_channels", 1))
        channels = 1 if max_channels < 2 else 2

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=channels,
            dtype="float32",
            device=device,
            callback=self._audio_callback,
            blocksize=int(self.sample_rate * AUDIO_BLOCK_SECONDS)
        )
        self.stream.start()

    def stop_recording(self) -> np.ndarray | None:
        """Encerra a gravação e retorna array 1D float32 ou None se for inaudível/curto."""
        if not self.is_recording:
            return None

        self.is_recording = False
        self.silence_callback = None

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        with self._lock:
            if not self.audio_frames:
                return None
            full_audio = np.concatenate(self.audio_frames, axis=0)
            self.audio_frames = []

        if full_audio.ndim > 1 and full_audio.shape[1] > 1:
            full_audio = np.mean(full_audio, axis=1)
        elif full_audio.ndim > 1:
            full_audio = full_audio.flatten()

        duration = len(full_audio) / self.sample_rate
        if duration < 0.4:
            return None

        return full_audio
