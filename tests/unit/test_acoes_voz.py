"""
Testes Unitários: Parser de Ações e Comandos de Voz.
Valida a extração da tag [[ENTER]] e higienização do texto a ser digitado.
"""

from src.ai.actions import VoiceActionParser


class TesteParserAcoesVoz:
    """Suíte de testes para identificação e separação de comandos de voz."""

    def test_deve_extrair_tag_enter_e_retornar_texto_limpo(self):
        """Valida se a tag [[ENTER]] é detectada e removida da mensagem."""
        texto_com_comando = "Por favor, atualize o layout da tela. [[ENTER]]"
        texto_limpo, deve_dar_enter = VoiceActionParser.extract_enter_action(texto_com_comando)

        assert deve_dar_enter is True, "O parser deveria ter identificado a solicitação de Enter."
        assert texto_limpo == "Por favor, atualize o layout da tela.", "A tag [[ENTER]] deveria ter sido removida do texto final."

    def test_deve_manter_texto_intacto_quando_nao_houver_comando(self):
        """Valida que textos sem comando permanecem inalterados e sem flag de Enter."""
        texto_simples = "Apenas uma frase comum ditada pelo usuário."
        texto_limpo, deve_dar_enter = VoiceActionParser.extract_enter_action(texto_simples)

        assert deve_dar_enter is False, "Não deve acionar Enter quando a tag não estiver presente."
        assert texto_limpo == texto_simples, "O texto simples deve ser preservado exatamente como recebido."

    def test_deve_lidar_com_texto_vazio_ou_nulo(self):
        """Garante que entradas vazias não gerem exceções."""
        texto_limpo, deve_dar_enter = VoiceActionParser.extract_enter_action("")
        assert texto_limpo == "", "Texto vazio deve retornar string vazia."
        assert deve_dar_enter is False, "Texto vazio não deve acionar Enter."

    def test_deve_identificar_ordem_explicita_de_enter(self):
        """Valida detecção de comandos falados para pressionar enter."""
        assert VoiceActionParser.has_explicit_enter_request("manda o texto e dar enter") is True
        assert VoiceActionParser.has_explicit_enter_request("pode enviar mensagem") is True
        assert VoiceActionParser.has_explicit_enter_request("tô com um bug aqui no consagrado") is False

    def test_deve_bloquear_alucinacao_de_enter_se_usuario_nao_pediu(self):
        """Garante que a tag [[ENTER]] seja removida se o usuário não pediu na fala original."""
        fala_original = "Estou com o bug, dentro do consagrado, e preciso de ajuda."
        texto_ia_alucinado = "Tô com um bug aqui no consagrado e preciso de ajuda. [[ENTER]]"

        sanitizado = VoiceActionParser.sanitize_enter_action(texto_ia_alucinado, raw_spoken_text=fala_original)
        assert "[[ENTER]]" not in sanitizado, "A tag [[ENTER]] alucinada deve ser removida quando o usuário não pediu."
        assert sanitizado == "Tô com um bug aqui no consagrado e preciso de ajuda."

    def test_deve_preservar_enter_quando_usuario_realmente_pediu(self):
        """Garante que a tag [[ENTER]] seja mantida se o usuário falou o comando explicitamente."""
        fala_original = "atualiza o botão e dar enter"
        texto_ia = "Atualiza o botão. [[ENTER]]"

        sanitizado = VoiceActionParser.sanitize_enter_action(texto_ia, raw_spoken_text=fala_original)
        assert "[[ENTER]]" in sanitizado, "A tag [[ENTER]] deve ser mantida quando o usuário pediu explicitamente."
