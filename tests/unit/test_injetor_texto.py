"""
Testes Unitários: Injetor de Texto e Clipboard.
Valida a integridade da área de transferência e o processamento de injeção.
"""

import pyperclip
from src.input.injector import inject_text


class TesteInjetorTexto:
    """Suíte de testes para injeção de texto e cópia para o clipboard."""

    def test_deve_armazenar_texto_corretamente_no_clipboard(self):
        """Valida se o texto injetado permanece copiado na área de transferência."""
        texto_teste = "TesteUnitario_OpenWhispr_12345"
        pyperclip.copy(texto_teste)

        leitura = pyperclip.paste()
        assert leitura == texto_teste, f"O clipboard deveria conter '{texto_teste}', mas continha '{leitura}'."

    def test_deve_ignorar_injecao_quando_texto_for_vazio(self):
        """Garante que entradas vazias não alterem o clipboard desnecessariamente."""
        pyperclip.copy("ConteudoPrevio")
        inject_text("")

        leitura = pyperclip.paste()
        assert leitura == "ConteudoPrevio", "Injeção com string vazia não deve sobrescrever o clipboard anterior."
