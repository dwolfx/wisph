"""
Módulo de injeção de texto no Windows.
Emula teclas físicas nativas (Ctrl+V e Enter) através de hardware scan-codes.
"""

import time
import pyperclip
import ctypes
from src.ai.actions import VoiceActionParser

user32 = ctypes.windll.user32

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_LWIN = 0x5B
VK_V = 0x56
VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002

SCAN_CTRL = 0x1D
SCAN_V = 0x2F
SCAN_ENTER = 0x1C


def release_modifier_keys():
    """Garante que teclas modificadoras presas sejam liberadas."""
    for vk in [VK_MENU, VK_SHIFT, VK_LWIN, VK_CONTROL]:
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def send_ctrl_v():
    """Simula pressionamento limpo de Ctrl+V com códigos de varredura de hardware."""
    release_modifier_keys()
    time.sleep(0.04)

    user32.keybd_event(VK_CONTROL, SCAN_CTRL, 0, 0)
    time.sleep(0.03)

    user32.keybd_event(VK_V, SCAN_V, 0, 0)
    time.sleep(0.05)

    user32.keybd_event(VK_V, SCAN_V, KEYEVENTF_KEYUP, 0)
    time.sleep(0.03)

    user32.keybd_event(VK_CONTROL, SCAN_CTRL, KEYEVENTF_KEYUP, 0)


def send_enter():
    """Simula envio da tecla Enter."""
    time.sleep(0.08)
    user32.keybd_event(VK_RETURN, SCAN_ENTER, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_RETURN, SCAN_ENTER, KEYEVENTF_KEYUP, 0)


def inject_text(text: str):
    """Copia o texto para a área de transferência e envia comando de colagem."""
    if not text:
        return

    clean_text, trigger_enter = VoiceActionParser.extract_enter_action(text)
    print(f"[Injetor] Injetando no cursor: '{clean_text}' (Auto-Enter: {trigger_enter})")

    try:
        pyperclip.copy(clean_text)
        time.sleep(0.06)
        send_ctrl_v()

        if trigger_enter:
            send_enter()
            print("[Injetor] ↵ Tecla Enter disparada com sucesso!")

        print("[Injetor] Texto injetado com sucesso!")
    except Exception as e:
        print(f"[Injetor Erro]: {e}")
