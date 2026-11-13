"""
Módulo de transcrição local rápida via faster-whisper.
"""

import time
import numpy as np

from src.config.settings import (
    DEFAULT_WHISPER_MODEL,
    WHISPER_LANGUAGE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_INITIAL_PROMPT
)

GHOST_HALLUCINATIONS = {
    "o que é isso", "o que é isso?", "o que é isso.",
    "obrigado", "obrigado.", "obrigado por assistir", "obrigada",
    "tchau", "tchau.", "legendas", "subtitles", "você", "..."
}


class WhisperTranscriber:
    def __init__(
        self,
        model_size: str = DEFAULT_WHISPER_MODEL,
        language: str = WHISPER_LANGUAGE,
        device: str = WHISPER_DEVICE,
        compute_type: str = WHISPER_COMPUTE_TYPE
    ):
        self.model_size = model_size
        self.language = language
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def load_model(self):
        """Carrega o modelo do Whisper na memória (cached)."""
        if self.model is None:
            from faster_whisper import WhisperModel
            print(f"[Whisper] Carregando modelo '{self.model_size}' na {self.device.upper()} ({self.compute_type})...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=4
            )
            print("[Whisper] Modelo pronto!")
        return self.model

    def transcribe(self, audio_data: np.ndarray | str) -> str:
        """Transcreve áudio direto de array numpy ou caminho de arquivo."""
        t0 = time.time()
        model = self.load_model()

        try:
            segments, info = model.transcribe(
                audio_data,
                language=self.language,
                beam_size=5,
                initial_prompt=WHISPER_INITIAL_PROMPT,
                vad_filter=True,
                vad_parameters=dict(threshold=0.6, min_speech_duration_ms=450)
            )

            text_parts = []
            for segment in segments:
                if segment.no_speech_prob > 0.55 or segment.avg_logprob < -1.1:
                    continue

                clean_seg = segment.text.strip()
                if clean_seg.lower() in GHOST_HALLUCINATIONS:
                    continue

                text_parts.append(clean_seg)

            full_text = " ".join(text_parts).strip()

            if full_text.lower() in GHOST_HALLUCINATIONS:
                print(f"[Whisper] Alucinação de ruído descartada: '{full_text}'")
                return ""

            elapsed = time.time() - t0
            if full_text:
                print(f"[Whisper] Transcrito em {elapsed:.2f}s: '{full_text}'")
            return full_text
        except Exception as e:
            print(f"[Whisper Erro]: {e}")
            return ""
