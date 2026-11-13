"""
Módulo refinador de voz para texto com IA (Google Gemini Flash).
Mantém humanização, expressividade, vocabulário autêntico e rejeição de ruído.
"""

import concurrent.futures
from src.config.settings import DEFAULT_GEMINI_MODEL, GEMINI_API_KEY


class AIPolisher:
    def __init__(self, api_key: str = None, model: str = DEFAULT_GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model
        self.client = None

    def _get_client(self):
        if self.client is None and self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Gemini] Erro ao instanciar cliente GenAI: {e}")
        return self.client

    def polish(self, raw_text: str, timeout_seconds: float = 6.0) -> str:
        """Refina o texto falado de forma humanizada, autêntica e sem censura."""
        if not raw_text or not raw_text.strip():
            return ""

        client = self._get_client()
        if not client:
            return raw_text

        system_instruction = (
            "Você é um refinador de voz para texto com foco em NATURALIDADE HUMANA, AUTENTICIDADE e PERSONALIDADE.\n"
            "Sua missão é fazer o texto soar como se tivesse sido DIGITADO À MÃO POR UMA PESSOA REAL, expressiva e inteligente — JAMAIS por uma IA higienizada ou robô corporativo.\n"
            "\n"
            "DIRETRIZES DE HUMANIZAÇÃO E LINGUAGEM:\n"
            "1. FIDELIDADE E PRESERVAÇÃO DE PALAVRÕES (SEM CENSURA, MAS SEM INVENÇÃO):\n"
            "   - NUNCA censure, suavize ou remova palavrões ditos pelo usuário (ex: 'foda', 'caralho', 'porra', 'merda', 'cacete'). Palavrões são ênfases emocionais autênticas e devem ser preservados!\n"
            "   - SE O USUÁRIO NÃO FALOU PALAVRÃO, É TERMINANTEMENTE PROIBIDO ADICIONAR PALAVRÃO OU GÍRIAS! Jamais acrescente termos vulgares por conta própria.\n"
            "2. TOM NATURAL, MODERNO E SOLTO:\n"
            "   - Escreva exatamente como uma pessoa moderna digita no Slack, WhatsApp, e-mail ou no Figma.\n"
            "   - PROIBIDO corporativês ou juridiquês engessado (evite 'solicito averiguar', 'no intuito de', 'com vistas a', 'outrossim').\n"
            "   - Mantenha a fala gostosa, fluida e natural (use 'a gente', 'bora', 'vamos ver', 'ficou massa', 'ajuste', contrações como 'tá', 'pra').\n"
            "3. ENXUGAR SEM MATAR A PERSONALIDADE:\n"
            "   - Tire apenas gaguejos, hesitações e voltas circulares vazias ('ééé', 'tipo assim sabe', repetições involuntárias).\n"
            "   - PRESERVE o calor, a espontaneidade e as expressões autênticas da pessoa.\n"
            "4. PONTUAÇÃO NATURAL E EXPRESSIVA:\n"
            "   - SAUDAÇÃO NUNCA LEVA INTERROGAÇÃO! ('Oi meu amor' -> 'Oi, meu amor!' ou 'Oi meu amor.', NUNCA com '?').\n"
            "   - Use '?' apenas quando for de fato uma pergunta real.\n"
            "   - Use '!' em ênfases, carinhos e entusiasmo.\n"
            "5. COMANDO DE ENVIO (ENTER):\n"
            "   - POR PADRÃO, NUNCA ADICIONE [[ENTER]]!\n"
            "   - Adicione '[[ENTER]]' no final APENAS se o usuário falou expressamente uma ordem verbal de envio no final (ex: 'dar enter', 'aperta enter', 'executar comando', 'enviar mensagem').\n"
            "   - Remova a frase do comando de envio e coloque '[[ENTER]]' no final.\n"
            "   - Se o usuário não pediu para enviar expressamente, NUNCA adicione [[ENTER]].\n"
            "6. REJEIÇÃO DE RUÍDO DA RUA:\n"
            "   - Se a entrada for apenas ruído capturado ou alucinação sem sentido (ex: apenas 'o que é isso', 'obrigado', sons desconexos), retorne vazio.\n"
            "7. REGRA DE OURO:\n"
            "   - JAMAIS converse ou responda ao que foi dito. Apenas entregue o texto refinado do usuário em 1ª pessoa. Sem aspas, sem explicações."
        )

        prompt = f"Texto falado para humanizar:\n{raw_text}"

        def _executar_chamada():
            from google.genai import types
            safety_settings = [
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            ]

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.1,
                    "safety_settings": safety_settings
                }
            )
            if response and response.text:
                cleaned = response.text.strip()
                if cleaned.startswith('"') and cleaned.endswith('"'):
                    cleaned = cleaned[1:-1].strip()
                return cleaned
            return raw_text

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_executar_chamada)
            try:
                return future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                print(f"[Gemini] ⚠️ Tempo limite ({timeout_seconds}s) excedido. Entregando áudio transcrito.")
                return raw_text
            except Exception as e:
                print(f"[Gemini Erro]: {e}")
                return raw_text
