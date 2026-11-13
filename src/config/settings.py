"""
Módulo de configurações centrais do OpenWhispr Windows.
Concentra parâmetros de áudio, modelos e atalhos.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Áudio e Microfone
SAMPLE_RATE = 16000
AUDIO_BLOCK_SECONDS = 0.05
LOW_CUT_FREQUENCY_HZ = 200.0

# Detecção de Atividade de Voz (VAD)
SILENCE_THRESHOLD_RMS = 0.016
SILENCE_DURATION_SECONDS = 0.9
MIN_SUSTAINED_VOICE_FRAMES = 5
MIN_SPEECH_DURATION_SECONDS = 0.5

# Transcrição (Whisper)
DEFAULT_WHISPER_MODEL = "base"
WHISPER_LANGUAGE = "pt"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_INITIAL_PROMPT = "Transcrição de voz em português brasileiro natural, com pontuação correta e vocabulário claro."

# IA Polisher (Gemini)
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Atalhos Globais
HOTKEY_DIRECT = "ctrl+shift+space"
HOTKEY_SMART = "ctrl+alt+space"
HOTKEY_HANDS_FREE = "ctrl+alt+h"
