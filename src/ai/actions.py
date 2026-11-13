"""
Parser e extrator de comandos de voz embutidos no texto.
Garante que a tecla Enter só seja acionada quando expressamente solicitada.
"""

TAG_ENTER = "[[ENTER]]"

GATILHOS_ENTER = (
    "dar enter",
    "dar um enter",
    "da enter",
    "aperta enter",
    "apertar enter",
    "pressiona enter",
    "pressionar enter",
    "bate enter",
    "bater enter",
    "enviar mensagem",
    "envia mensagem",
    "enviar agora",
    "pode enviar",
    "executar comando",
    "executa comando",
    "e envia",
    "e enviar"
)


class VoiceActionParser:
    """Extrai gatilhos de ação física (como tecla Enter) do texto gerado."""

    @staticmethod
    def has_explicit_enter_request(spoken_text: str) -> bool:
        """Verifica se o áudio original falado continha solicitação explícita de Enter."""
        if not spoken_text:
            return False
        texto_norm = spoken_text.lower().strip()
        return any(gatilho in texto_norm for gatilho in GATILHOS_ENTER)

    @staticmethod
    def sanitize_enter_action(polished_text: str, raw_spoken_text: str = None) -> str:
        """
        Se a IA inseriu [[ENTER]], valida se o usuário realmente pediu na fala original.
        Se não pediu, remove a tag [[ENTER]] para impedir envio indevido.
        """
        if not polished_text:
            return ""

        if TAG_ENTER in polished_text:
            if raw_spoken_text is not None and not VoiceActionParser.has_explicit_enter_request(raw_spoken_text):
                # Usuário não solicitou envio na fala original; descarta tag indevida
                return polished_text.replace(TAG_ENTER, "").strip()

        return polished_text

    @staticmethod
    def extract_enter_action(text: str) -> tuple[str, bool]:
        """
        Verifica se a tag [[ENTER]] está presente.
        Retorna (texto_limpo, deve_pressionar_enter).
        """
        if not text:
            return "", False

        if TAG_ENTER in text:
            clean_text = text.replace(TAG_ENTER, "").strip()
            return clean_text, True

        return text.strip(), False

