"""
Script PyInstaller para compilar o OpenWhispr em executável único para Windows.
"""

import subprocess
import sys


def build_exe():
    print("[Build] Compilando OpenWhispr Windows para executável único...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=OpenWhispr",
        "--add-data=src/ui/styles;src/ui/styles",
        "--collect-all=faster_whisper",
        "--collect-all=ctranslate2",
        "--collect-all=sounddevice",
        "--collect-all=google.genai",
        "--hidden-import=pyside6",
        "--hidden-import=keyboard",
        "--hidden-import=pyperclip",
        "main.py"
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n🎉 [Build] Sucesso! Executável gerado na pasta dist/OpenWhispr/OpenWhispr.exe")
    else:
        print(f"\n❌ [Build] Falha na compilação. Código: {result.returncode}")


if __name__ == "__main__":
    build_exe()
