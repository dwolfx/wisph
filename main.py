"""
OpenWhispr Windows (Voice Flow)
Ponto de entrada principal da aplicação.
"""

import sys
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from src.core.controller import VoiceFlowController

# Garante saída sem buffer no console do Windows
if sys.platform == "win32":
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True, errors="replace")
    if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True, errors="replace")

load_dotenv()


def main():
    print("==================================================")
    print("🎙️ Iniciando OpenWhispr Windows (Voice Flow)...")
    print("==================================================")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    controller = VoiceFlowController(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
