"""
Testes Unitários: Detector de Atividade de Voz (VAD).
Valida o cálculo de RMS, a rejeição de cliques isolados e a detecção de pausas.
"""

import time
import numpy as np
from src.audio.vad import VoiceActivityDetector


class TesteDetectorAtividadeVoz:
    """Suíte de testes para a lógica de VAD e energia vocal sustentada."""

    def test_deve_calcular_rms_corretamente_para_bloco_silencioso(self):
        """Valida se bloco de silêncio absoluto retorna RMS zero."""
        bloco_vazio = np.zeros(800, dtype=np.float32)
        rms = VoiceActivityDetector.calculate_rms(bloco_vazio)
        assert rms == 0.0, "O RMS de um bloco zerado deve ser exatamente 0.0."

    def test_deve_rejeitar_estalo_curto_de_teclado_sem_ativar_fala(self):
        """Garante que um clique de tecla mecânica não ative o estado de voz."""
        vad = VoiceActivityDetector(silence_threshold=0.016, min_sustained_frames=5)
        vad.reset()

        # Envia 1 bloco com estalo forte (0.040) e 4 blocos de silêncio (0.002)
        voz_ativa, deve_parar = vad.process_block(0.040)
        assert not voz_ativa, "Um único estalo de teclado não pode marcar a voz como ativa."

        for _ in range(4):
            voz_ativa, deve_parar = vad.process_block(0.002)

        assert not voz_ativa, "O VAD não deve ativar voz para ruídos transitórios curtos."
        assert not deve_parar, "Não deve disparar auto-stop para ruídos que nunca foram fala válida."

    def test_deve_ativar_voz_quando_houver_fala_sustentada(self):
        """Valida se pelo menos 5 blocos sustentados ativam o estado de voz."""
        vad = VoiceActivityDetector(silence_threshold=0.016, min_sustained_frames=5)
        vad.reset()

        voz_ativa = False
        for _ in range(5):
            voz_ativa, _ = vad.process_block(0.025)

        assert voz_ativa, "Após 5 blocos consecutivos de fala, o estado de voz deve ser ativado."

    def test_deve_disparar_parada_automatica_apos_pausa_no_silencio(self):
        """Valida se uma pausa no silêncio dispara o gatilho de auto-stop."""
        vad = VoiceActivityDetector(silence_threshold=0.016, silence_duration=0.2, min_sustained_frames=3)
        vad.reset()
        vad._start_time = time.time() - 1.0  # Simula que já gravou mais de 0.5s

        # Ativa a fala
        for _ in range(3):
            vad.process_block(0.030)

        # Espera a duração de silêncio passar
        time.sleep(0.25)
        _, deve_parar = vad.process_block(0.002)

        assert deve_parar, "O VAD deve disparar a parada automática após a pausa de silêncio configurada."
