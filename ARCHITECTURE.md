# Arquitetura Técnica — OpenWhispr Windows (`wisph`)

Este documento detalha o pipeline de áudio, transcrição neural local, refinamento via LLM e injeção de teclado em nível de hardware do **OpenWhispr Windows**.

---

## 1. Visão Geral do Pipeline

```text
[Microfone (16kHz Mono)]
       │
       ▼
[Filtro Passa-Alta 200Hz (src/audio/filters.py)]
       │
       ▼
[Sustained Speech Gate & VAD (src/audio/vad.py)]
       │
       ▼
[Transcrição Local faster-whisper (src/speech/transcriber.py)]
       │
       ├──► (Modo Direto: Ctrl+Shift+Space) ──────────────────────┐
       │                                                          │
       └──► (Modo Smart: Ctrl+Alt+Space)                          ▼
            [Polisher Gemini Flash (src/ai/polisher.py)] ──► [Extrator de Comandos (src/ai/actions.py)]
                                                                  │
                                                                  ▼
                                                     [Injetor Win32 Scan-Codes (src/input/injector.py)]
```

---

## 2. Módulos Principais

### 2.1. Engenharia de Áudio (`src/audio/`)
* **`filters.py`**: Aplica um filtro passa-alta Butterworth em 200 Hz para eliminar ruídos graves de baixa frequência (trânsito, ventiladores, ar-condicionado e batidas na mesa) sem afetar os harmônicos da voz humana.
* **`vad.py`**: Implementa detecção de atividade de voz com *Sustained Speech Gate* (exige ao menos 250 ms contínuos de fala para evitar falsos positivos com cliques de mouse/teclado) e auto-stop após 0.9s de silêncio.
* **`recorder.py`**: Captura streams de áudio em memória via `sounddevice` com baixa latência.

### 2.2. Transcrição Local (`src/speech/transcriber.py`)
* Baseado no **`faster-whisper`** (CTranslate2), mantendo o modelo carregado em memória para transcrição quase instantânea e 100% offline no modo direto.

### 2.3. Refinamento Inteligente & Comandos (`src/ai/`)
* **`polisher.py`**: Quando acionado no modo Smart (`Ctrl + Alt + Espaço`), envia a transcrição bruta para o **Gemini Flash** para pontuação natural, correção gramatical sutil e formatação concisa, preservando o tom e vocabulário original do usuário.
* **`actions.py`**: Detecta intenções finais por voz (como *"enviar"*, *"executar"*, *"executar comando"*) e as converte em tokens de ação (`[[ENTER]]`) executados automaticamente após colar o texto.

### 2.4. Injeção de Input & Atalhos (`src/input/`)
* **`hotkeys.py`**: Listener global de atalhos de teclado no Windows.
* **`injector.py`**: Injeta o texto transcrito diretamente na janela ativa utilizando área de transferência + eventos de teclado Win32 com hardware scan-codes para compatibilidade com qualquer IDE, terminal ou navegador.

### 2.5. Interface Gráfica (`src/ui/` & `src/core/`)
* Construída em **PyQt6**, com uma pílula flutuante translúcida (`pill.qss`) que renderiza ondas sonoras a 60fps e ícone na bandeja do sistema (`tray.py`) orquestrados de forma thread-safe por sinais Qt (`src/core/signals.py` e `src/core/controller.py`).

---

## 3. Configuração e Execução

1. Copie `.env.example` para `.env` e preencha sua `GEMINI_API_KEY` (opcional para o modo Direto, necessária para o modo Smart).
2. Instale as dependências no ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Execute com `run.bat` (ou `run-debug.bat` para visualizar logs no console).
4. Para gerar um executável standalone do Windows, execute `python build.py`.
