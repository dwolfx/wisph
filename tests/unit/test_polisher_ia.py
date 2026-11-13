"""
Testes Unitários: Refinador de IA (Gemini Flash).
Valida remoção de prolixidade, preservação de palavrões, saudações sem interrogação e comando de Enter.
"""

from src.ai.polisher import AIPolisher


class TestePolisherIA:
    """Suíte de testes para a inteligência de refinamento de voz para texto."""

    def test_deve_retornar_vazio_quando_texto_for_vazio(self):
        """Garante que entradas em branco retornem string vazia sem chamar a API."""
        polisher = AIPolisher()
        resultado = polisher.polish("")
        assert resultado == "", "Texto de entrada vazio deve retornar imediatamente vazio."

    def test_deve_refinar_prolixidade_e_preservar_sentido_da_frase(self):
        """Valida se o Gemini enxuga redundâncias mantendo a primeira pessoa."""
        polisher = AIPolisher()
        entrada = "entao eu queria ver se a gente podia marcar uma reuniao amanha as dez pra conversar"
        resultado = polisher.polish(entrada)

        assert len(resultado) > 0, "O resultado do polimento não pode ser vazio."
        assert "reunião" in resultado.lower(), "O assunto principal (reunião) deve estar presente no texto refinado."
        assert "dez" in resultado.lower(), "O horário 'dez' deve ser preservado na frase."

    def test_deve_preservar_palavroes_sem_censura(self):
        """Garante que palavras de ênfase e palavrões não sejam censurados com asteriscos ou removidos."""
        polisher = AIPolisher()
        entrada = "cara ficou foda esse novo layout que voce fez"
        resultado = polisher.polish(entrada)

        assert "foda" in resultado.lower(), "A palavra de ênfase 'foda' deve ser mantida fielmente sem censura."

    def test_deve_evitar_interrogacao_em_saudacoes(self):
        """Valida que saudações carinhosas não recebam ponto de interrogação."""
        polisher = AIPolisher()
        entrada = "oi meu amor"
        resultado = polisher.polish(entrada)

        assert "?" not in resultado, f"A saudação 'oi meu amor' não pode ter interrogação. Resultado: {resultado}"
        assert "amor" in resultado.lower(), "O vocativo 'amor' deve ser mantido."

    def test_nao_deve_adicionar_palavroes_quando_usuario_nao_falou(self):
        """Garante que a IA não invente xingamentos em falas neutras do usuário."""
        polisher = AIPolisher()
        entrada = "Estou com o bug, dentro do consagrado, e preciso de ajuda."
        resultado = polisher.polish(entrada)

        palavroes = ["porra", "caralho", "merda", "foda", "cacete"]
        assert not any(p in resultado.lower() for p in palavroes), (
            f"A IA não deveria adicionar palavrões inventados. Retornou: '{resultado}'"
        )

    def test_nao_deve_adicionar_enter_em_fala_comum(self):
        """Garante que falas normais não recebam comando de envio [[ENTER]]."""
        polisher = AIPolisher()
        entrada = "Estou com o bug, dentro do consagrado, e preciso de ajuda."
        resultado = polisher.polish(entrada)

        assert "[[ENTER]]" not in resultado, (
            f"Falas comuns sem ordem expressa não podem conter [[ENTER]]. Retornou: '{resultado}'"
        )
