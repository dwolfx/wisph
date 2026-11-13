"""
Controlador central do Voice Flow.
Orquestra microfone, Whisper local, Gemini IA, injeção de texto e interface visual.
"""

import sys
import threading
import time

if sys.platform == "win32":
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, errors="replace")
    if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, errors="replace")

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication
import keyboard

from src.core.signals import ControllerSignals
from src.audio.recorder import AudioRecorder
from src.speech.transcriber import WhisperTranscriber
from src.ai.polisher import AIPolisher
from src.ai.actions import VoiceActionParser
from src.input.injector import inject_text
from src.input.hotkeys import HotkeyManager
from src.ui.components.pill_widget import FloatingPill
from src.ui.tray import SystemTray
from src.config.settings import (
    DEFAULT_WHISPER_MODEL,
    WHISPER_LANGUAGE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    HOTKEY_DIRECT,
    HOTKEY_SMART,
    HOTKEY_HANDS_FREE
)


class VoiceFlowController:
    def __init__(self, app: QApplication):
        self.app = app
        self.signals = ControllerSignals()

        # Motores
        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber(
            model_size=DEFAULT_WHISPER_MODEL,
            language=WHISPER_LANGUAGE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE
        )
        self.polisher = AIPolisher()

        self.hands_free_mode = False
        self.current_active_mode = "smart"
        self._is_processing = False

        # Interface
        self.pill = FloatingPill()
        self.tray = SystemTray(
            app=self.app,
            on_quit=self.shutdown,
            on_model_changed=self.change_model,
            on_mode_changed=self.change_hotkey_mode,
            on_hands_free_toggled=self.set_hands_free
        )

        # Atalhos
        self.hotkey_manager = HotkeyManager(
            direct_hotkey=HOTKEY_DIRECT,
            smart_hotkey=HOTKEY_SMART,
            mode="toggle"
        )
        self.hotkey_manager.set_callbacks(
            on_start=self.on_hotkey_start,
            on_stop=self.on_hotkey_stop
        )

        try:
            keyboard.add_hotkey(HOTKEY_HANDS_FREE, self.toggle_hands_free_hotkey, suppress=False)
        except Exception:
            pass

        self._connect_signals()

        threading.Thread(target=self._prewarm_whisper, daemon=True).start()
        self.hotkey_manager.start()

        print("\n✨ [OpenWhispr Windows] Pronto e aguardando!")
        print(f"🎙️ Ditado Direto: {HOTKEY_DIRECT} (1 toque -> fale -> pausa cola sozinho)")
        print(f"✨ Modo Smart (IA): {HOTKEY_SMART} (1 toque -> fale -> pausa cola sozinho)")
        print(f"🎧 Modo Mãos-Livres: {HOTKEY_HANDS_FREE} (escuta contínua com auto-paste)\n")

    def _connect_signals(self):
        self.signals.recording_started.connect(self.pill.show_listening)
        self.signals.amplitude_updated.connect(self.pill.set_amplitude)
        self.signals.transcribing_started.connect(self.pill.show_transcribing)
        self.signals.polishing_started.connect(self.pill.show_polishing)
        self.signals.finished.connect(self.on_transcription_finished)
        self.signals.cancel.connect(self._handle_cancel)
        self.signals.waiting_state.connect(lambda: self.pill.show_waiting(self.current_active_mode))

    def _prewarm_whisper(self):
        try:
            self.transcriber.load_model()
        except Exception as e:
            print(f"[Aviso] Erro no pré-carregamento do Whisper: {e}")

    def on_hotkey_start(self, mode: str):
        if self._is_processing:
            return
        self.current_active_mode = mode

        def amp_callback(amp):
            self.signals.amplitude_updated.emit(amp)
            if self.hands_free_mode and amp > 0.04 and self.pill.current_state == "waiting":
                self.signals.recording_started.emit(mode)

        def auto_silence_callback():
            print("\n[VAD] 🤫 Pausa natural detectada (0.9s)! Processando áudio...")
            self.hotkey_manager._is_recording = False
            self.hotkey_manager._current_mode = None
            self._process_pipeline(mode)

        if not self.hands_free_mode:
            self.signals.recording_started.emit(mode)
        else:
            self.signals.waiting_state.emit()

        self.recorder.start_recording(
            amplitude_callback=amp_callback,
            silence_callback=auto_silence_callback
        )

    def on_hotkey_stop(self, mode: str):
        print("\n[Atalho] Parada manual acionada.")
        threading.Thread(target=self._process_pipeline, args=(mode,), daemon=True).start()

    def _process_pipeline(self, mode: str):
        if self._is_processing:
            return
        self._is_processing = True

        try:
            audio_array = self.recorder.stop_recording()
            if audio_array is None or len(audio_array) == 0:
                print("[Pipeline] Nenhum áudio significativo capturado.")
                self.signals.cancel.emit()
                return

            duration = len(audio_array) / self.recorder.sample_rate
            print(f"[Pipeline] Áudio capturado ({duration:.1f}s). Transcrevendo com Whisper...")
            self.signals.transcribing_started.emit()

            try:
                raw_text = self.transcriber.transcribe(audio_array)
            except Exception as e:
                print(f"[Erro Whisper]: {e}")
                self.signals.cancel.emit()
                return

            if not raw_text or not raw_text.strip():
                print("[Whisper] Silêncio ou fala inaudível.")
                self.signals.cancel.emit()
                return

            final_text = raw_text
            if mode == "smart":
                print(f"[Gemini] Refinando transcrição: '{raw_text}'...")
                self.signals.polishing_started.emit()
                try:
                    polished = self.polisher.polish(raw_text)
                    final_text = VoiceActionParser.sanitize_enter_action(polished, raw_spoken_text=raw_text)
                    print(f"[Gemini] Texto formatado: '{final_text}'")
                except Exception as e:
                    print(f"[Erro Polisher]: {e}")
                    final_text = raw_text
            else:
                final_text = VoiceActionParser.sanitize_enter_action(raw_text, raw_spoken_text=raw_text)

            self.signals.finished.emit(final_text)
        finally:
            self._is_processing = False

    @Slot(str)
    def on_transcription_finished(self, text: str):
        self.pill.show_done(text, auto_hide=not self.hands_free_mode)
        threading.Thread(target=inject_text, args=(text,), daemon=True).start()

        if self.hands_free_mode:
            threading.Thread(target=self._restart_hands_free_delayed, daemon=True).start()

    def _handle_cancel(self):
        if self.hands_free_mode:
            self.signals.waiting_state.emit()
            threading.Thread(target=self._restart_hands_free_delayed, daemon=True).start()
        else:
            self.pill.hide()

    def _restart_hands_free_delayed(self):
        time.sleep(1.0)
        if self.hands_free_mode and not self._is_processing:
            print("[Mãos-Livres] 🎧 Aguardando próxima fala...")
            self.signals.waiting_state.emit()
            self.on_hotkey_start(self.current_active_mode)

    def toggle_hands_free_hotkey(self):
        self.set_hands_free(not self.hands_free_mode)

    def set_hands_free(self, enabled: bool):
        self.hands_free_mode = enabled
        print(f"\n[Modo Mãos-Livres] {'ATIVADO 🎧' if enabled else 'DESATIVADO ❌'}")
        if enabled:
            self.signals.waiting_state.emit()
            self.on_hotkey_start(self.current_active_mode)
        else:
            self.recorder.stop_recording()
            self.pill.hide()

    def change_model(self, model_name: str):
        print(f"[Config] Mudando modelo para: {model_name}")
        self.transcriber = WhisperTranscriber(model_size=model_name, language=WHISPER_LANGUAGE)
        threading.Thread(target=self.transcriber.load_model, daemon=True).start()

    def change_hotkey_mode(self, mode: str):
        print(f"[Config] Modo de atalho alterado para: {mode}")
        self.hotkey_manager.stop()
        self.hotkey_manager.mode = mode
        self.hotkey_manager.start()

    def shutdown(self):
        self.hotkey_manager.stop()
        if self.recorder.is_recording:
            self.recorder.stop_recording()
