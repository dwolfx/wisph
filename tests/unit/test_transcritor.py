"""
Testes Unitários: Transcritor Whisper Local.
Valida inicialização do modelo e processamento de áudio sintético na memória.
"""

import numpy as np
from src.speech.transcriber import WhisperTranscriber


class TesteTranscritorWhisper:
    """Suíte de testes para o motor de transcrição faster-whisper."""

    def test_deve_carregar_modelo_na_memoria_com_sucesso(self):
        """Valida se o Whisper inicializa o modelo sem erros de biblioteca DLL ou caminho."""
        transcritor = WhisperTranscriber(model_size="base", language="pt", device="cpu", compute_type="int8")
        modelo = transcritor.load_model()
        assert modelo is not None, "O modelo do faster-whisper deve ser carregado com sucesso."

    def test_deve_processar_array_numpy_direto_na_memoria(self):
        """Valida que a transcrição aceita buffer de áudio em memória sem necessitar de arquivo em disco."""
        transcritor = WhisperTranscriber(model_size="base", language="pt", device="cpu", compute_type="int8")

        # Gera 1 segundo de tom suave em memória
        taxa = 16000
        tempo = np.linspace(0, 1.0, taxa, endpoint=False)
        audio_sintetico = (0.01 * np.sin(2 * np.pi * 440 * tempo)).astype(np.float32)

        resultado = transcritor.transcribe(audio_sintetico)
        assert isinstance(resultado, str), "O retorno da transcrição deve ser uma string."
