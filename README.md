# 🎙️ OpenWhispr Windows (Voice Flow)

Assistente de ditado por voz inteligente para Windows — **100% gratuito, privado e ultra-rápido**.  
Inspirado no OpenWhispr / Wispr Flow / MacWhisper, feito sob medida por Victor Hugo & Maya! ❤️

---

## 🎯 Funcionalidades Principais
1. **Atalhos Globais no Windows**:
   - `Ctrl + Shift + Espaço`: **Ditado Direto** (Whisper Local em memória -> cola no cursor).
   - `Ctrl + Alt + Espaço`: **Modo Smart (IA)** (Whisper Local -> Gemini Flash humanizado e conciso -> cola formatado).
   - `Ctrl + Alt + H`: **Modo Mãos-Livres (Hands-Free)** (escuta contínua inteligente sem precisar de atalhos).
2. **Engenharia de Áudio Avançada**:
   - **Filtro Passa-Alta Acústico (200Hz Low-Cut)**: Corta 85% do ruído de trânsito, escapamento de carros e ar-condicionado.
   - **Sustained Speech Gate**: Exige >= 250ms de vibração vocal contínua para ignorar cliques de teclado e latidos distantes.
   - **Auto-Stop Natural (VAD)**: Detecta pausas de 0.9s na fala e cola automaticamente.
3. **Comandos de Ação por Voz**:
   - Diga *"enviar"*, *"executar"* ou *"executar comando"* no final para dar `Enter` automático.
4. **Interface Translúcida & System Tray**:
   - Pílula flutuante translúcida moderna com ondas sonoras a 60fps.
   - Menu na bandeja do Windows (System Tray) para seleção de modelos Whisper e modos.

---

## 📦 Arquitetura Modular (Diretrizes Globais)
```text
src/
├── config/settings.py       # Configurações centralizadas
├── audio/
│   ├── filters.py           # Filtro passa-alta acústico (200Hz)
│   ├── vad.py               # Detector de atividade de voz e pausas
│   └── recorder.py          # Captura do microfone sounddevice
├── ai/
│   ├── polisher.py          # Refinador humanizado Gemini Flash (sem censura)
│   └── actions.py           # Extrator de comandos de ação ([[ENTER]])
├── speech/transcriber.py    # Transcrição local faster-whisper
├── input/
│   ├── hotkeys.py           # Gerenciador global de atalhos
│   └── injector.py          # Injetor com hardware scan-codes
├── ui/
│   ├── styles/              # QSS dedicado e variáveis de tema
│   │   ├── theme.py
│   │   ├── pill.qss
│   │   └── tray.qss
│   ├── components/          # Componentes isolados (Pill e Waveform)
│   └── tray.py              # Ícone do System Tray
└── core/
    ├── signals.py           # Sinais assíncronos Qt
    └── controller.py        # Orquestrador mestre da aplicação
main.py                      # Ponto de entrada enxuto
```

---

## 🧪 Suíte de Testes (PT-BR)
Para executar todos os testes unitários e de integração:
```bash
pytest -v
```
Ou dê dois cliques em `test.bat`.
