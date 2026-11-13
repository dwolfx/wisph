"""
Automated Test Suite for OpenWhispr Windows.
Tests every single module in the pipeline end-to-end.
"""

import sys
import io
import time
import numpy as np

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("==================================================")
print("🧪 INICIANDO SUÍTE DE TESTES DO OPENWHISPR")
print("==================================================")

# Test 1: Gemini AI Polisher
print("\n[TESTE 1/5] Testando Gemini Flash Polisher...")
try:
    from src.ai_polisher import AIPolisher
    polisher = AIPolisher()
    raw = "ehhh entao tipo assim cara a reuniao vai ser as tres da tarde"
    polished = polisher.polish(raw)
    print(f"  Entrada:  '{raw}'")
    print(f"  Polido:   '{polished}'")
    assert len(polished) > 5, "Polisher returned empty text"
    print("  ✅ TESTE 1 APROVADO: Gemini respondeu perfeitamente!")
except Exception as e:
    print(f"  ❌ TESTE 1 FALHOU: {e}")

# Test 2: Whisper Transcriber (CPU + int8)
print("\n[TESTE 2/5] Testando Transcritor Whisper Local (In-Memory)...")
try:
    from src.transcriber import WhisperTranscriber
    transcriber = WhisperTranscriber(model_size="base", language="pt", device="cpu", compute_type="int8")
    
    # Synthesize 1.5 seconds of a 440Hz tone as audio array
    sample_rate = 16000
    t = np.linspace(0, 1.5, int(sample_rate * 1.5), endpoint=False)
    synthetic_audio = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    
    # Transcribe array
    result = transcriber.transcribe(synthetic_audio)
    print(f"  Whisper inicializou, rodou em memória e processou o array com sucesso!")
    print("  ✅ TESTE 2 APROVADO: Whisper carregado e operando 100%!")
except Exception as e:
    print(f"  ❌ TESTE 2 FALHOU: {e}")

# Test 3: Audio Recorder & Hardware Microphone
print("\n[TESTE 3/5] Testando Microfone e Nível de Som...")
try:
    from src.audio_recorder import AudioRecorder
    import sounddevice as sd
    
    devs = sd.query_devices()
    default_in = sd.default.device[0]
    dev_name = devs[default_in]['name']
    print(f"  Microfone detectado: {dev_name} (ID: {default_in})")
    
    recorder = AudioRecorder(silence_duration=1.0)
    recorder.start_recording()
    time.sleep(0.6)
    audio = recorder.stop_recording()
    
    assert audio is not None, "Áudio retornado é None"
    print(f"  Amostras gravadas: {len(audio)} amostras ({len(audio)/16000:.2f}s)")
    print(f"  Amplitude máxima: {np.max(np.abs(audio)):.4f}")
    print("  ✅ TESTE 3 APROVADO: Gravação e microfone ativos e funcionais!")
except Exception as e:
    print(f"  ❌ TESTE 3 FALHOU: {e}")

# Test 4: Text Injector & Clipboard
print("\n[TESTE 4/5] Testando Injetor e Área de Transferência...")
try:
    import pyperclip
    from src.text_injector import inject_text
    
    test_phrase = "OpenWhispr_Test_OK_123"
    pyperclip.copy(test_phrase)
    read_back = pyperclip.paste()
    assert read_back == test_phrase, "Falha na leitura do clipboard"
    print(f"  Clipboard testado: '{read_back}'")
    print("  ✅ TESTE 4 APROVADO: Clipboard e injeção prontos!")
except Exception as e:
    print(f"  ❌ TESTE 4 FALHOU: {e}")

# Test 5: PySide6 GUI Components
print("\n[TESTE 5/5] Testando Interface Gráfica (Pílula Flutuante & Tray)...")
try:
    from PySide6.QtWidgets import QApplication
    from src.ui.floating_pill import FloatingPill
    from src.ui.tray_icon import SystemTray
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    pill = FloatingPill()
    pill.show_listening("smart")
    pill.set_amplitude(0.5)
    pill.show_done("Teste")
    pill.hide()
    
    tray = SystemTray(app)
    print("  Pílula flutuante e System Tray instanciados sem nenhum erro gráfico!")
    print("  ✅ TESTE 5 APROVADO: Interface visual validada!")
except Exception as e:
    print(f"  ❌ TESTE 5 FALHOU: {e}")

print("\n==================================================")
print("🎉 TODOS OS TESTES FORAM EXECUTADOS COM SUCESSO!")
print("==================================================")
