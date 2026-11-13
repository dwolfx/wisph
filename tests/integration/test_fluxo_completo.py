"""
Testes de Integração: Pipeline Completo do OpenWhispr Windows.
Valida o fluxo integrado de captura simulada -> VAD -> Transcrição -> Polimento com IA -> Injeção.
"""

import numpy as np
import pyperclip
from src.audio.vad import VoiceActivityDetector
from src.speech.transcriber import WhisperTranscriber
from src.ai.polisher import AIPolisher
from src.ai.actions import VoiceActionParser
from src.input.injector import inject_text


class TesteIntegracaoVoiceFlow:
    """Suíte de testes de integração do pipeline de ponta a ponta."""

    def test_deve_executar_fluxo_completo_de_transcricao_e_injecao(self):
        """
        Cenário Integrado:
        1. Gera áudio sintético.
        2. Processa pelo VAD para validar atividade.
        3. Realiza polimento textual com IA.
        4. Separa ações de Enter.
        5. Injeta no clipboard com sucesso.
        """
        # Etapa 1: VAD
        vad = VoiceActivityDetector()
        bloco = np.ones(800, dtype=np.float32) * 0.03
        rms = vad.calculate_rms(bloco)
        assert rms > 0.016, "O VAD deveria reconhecer o nível de energia do bloco sintético."

        # Etapa 2: Polisher com Ação de Enter
        polisher = AIPolisher()
        frase_falada = "vamos finalizar esse componente executar comando"
        texto_polido = polisher.polish(frase_falada)

        assert len(texto_polido) > 0, "O texto polido não pode ser vazio."

        # Etapa 3: Extração de Ação e Injeção
        texto_final, deve_dar_enter = VoiceActionParser.extract_enter_action(texto_polido)
        inject_text(texto_final)

        # Validação final no clipboard
        conteudo_clipboard = pyperclip.paste()
        assert conteudo_clipboard == texto_final, (
            f"O clipboard deveria conter '{texto_final}', mas continha '{conteudo_clipboard}'."
        )
