"""
Gerenciador de atalhos globais de teclado no Windows.
Suporta modos Alternar (Toggle) e Push-To-Talk com proteção contra debounce.
"""

import threading
import time
import keyboard

from src.config.settings import HOTKEY_DIRECT, HOTKEY_SMART


class HotkeyManager:
    def __init__(self, direct_hotkey: str = HOTKEY_DIRECT, smart_hotkey: str = HOTKEY_SMART, mode: str = "toggle"):
        self.direct_hotkey = direct_hotkey
        self.smart_hotkey = smart_hotkey
        self.mode = mode
        
        self.on_start = None
        self.on_stop = None
        
        self._is_recording = False
        self._current_mode = None
        self._running = False
        self._last_toggle_time = 0.0

    def set_callbacks(self, on_start, on_stop):
        self.on_start = on_start
        self.on_stop = on_stop

    def start(self):
        """Registra os atalhos no sistema operacional."""
        if self._running:
            return
        self._running = True

        if self.mode == "toggle":
            keyboard.add_hotkey(self.direct_hotkey, lambda: self._handle_toggle("direct"), suppress=False)
            keyboard.add_hotkey(self.smart_hotkey, lambda: self._handle_toggle("smart"), suppress=False)
        else:
            self._setup_push_to_talk()

    def _handle_toggle(self, mode_type: str):
        now = time.time()
        if now - self._last_toggle_time < 0.5:
            return
        self._last_toggle_time = now

        if not self._is_recording:
            self._is_recording = True
            self._current_mode = mode_type
            print(f"\n[Atalho] 🎙️ Gravação INICIADA (Modo: {mode_type.upper()})")
            if self.on_start:
                self.on_start(mode_type)
        else:
            current = self._current_mode
            self._is_recording = False
            self._current_mode = None
            print(f"[Atalho] ⏹️ Gravação PARADA (Modo: {current.upper()})")
            if self.on_stop:
                self.on_stop(current)

    def _setup_push_to_talk(self):
        def ptt_listener():
            while self._running:
                for mode_type, hk in [("direct", self.direct_hotkey), ("smart", self.smart_hotkey)]:
                    if keyboard.is_pressed(hk):
                        if not self._is_recording:
                            self._is_recording = True
                            self._current_mode = mode_type
                            if self.on_start:
                                self.on_start(mode_type)
                            while keyboard.is_pressed(hk) and self._running:
                                time.sleep(0.04)
                            self._is_recording = False
                            self._current_mode = None
                            if self.on_stop:
                                self.on_stop(mode_type)
                time.sleep(0.04)

        t = threading.Thread(target=ptt_listener, daemon=True)
        t.start()

    def stop(self):
        """Desregistra todos os atalhos."""
        self._running = False
        try:
            keyboard.unhook_all()
        except Exception:
            pass
