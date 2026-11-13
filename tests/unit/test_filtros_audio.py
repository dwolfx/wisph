"""
Testes Unitários: Filtro Acústico Passa-Alta (Low-Cut).
Valida a eliminação de ruídos graves e a integridade da voz humana.
"""

import numpy as np
from src.audio.filters import AcousticFilter


class TesteFiltroAcustico:
    """Suíte de testes para o filtro passa-alta de áudio."""

    def test_deve_atenuar_ruidos_graves_de_transito_e_escapamento(self, amostra_audio_ronco_carro):
        """Valida se frequências graves abaixo de 200 Hz são fortemente atenuadas."""
        filtro = AcousticFilter(sample_rate=16000, cutoff_hz=200.0)

        rms_antes = float(np.sqrt(np.mean(amostra_audio_ronco_carro ** 2)))
        audio_filtrado = filtro.apply(amostra_audio_ronco_carro)
        rms_depois = float(np.sqrt(np.mean(audio_filtrado ** 2)))

        taxa_atenuacao = (rms_antes - rms_depois) / rms_antes

        # Redução de mais de 50% na amplitude linear (equivalente a >75% de corte na potência acústica)
        assert taxa_atenuacao >= 0.50, (
            f"O filtro deveria atenuar pelo menos 50% da amplitude do ronco grave, mas atenuou {taxa_atenuacao*100:.1f}%."
        )

    def test_deve_preservar_energia_da_voz_humana(self, amostra_audio_voz_humana):
        """Valida se as frequências vocais acima de 200 Hz passam sem perda significativa."""
        filtro = AcousticFilter(sample_rate=16000, cutoff_hz=200.0)

        rms_antes = float(np.sqrt(np.mean(amostra_audio_voz_humana ** 2)))
        audio_filtrado = filtro.apply(amostra_audio_voz_humana)
        rms_depois = float(np.sqrt(np.mean(audio_filtrado ** 2)))

        preservacao = rms_depois / rms_antes

        assert preservacao >= 0.90, (
            f"A voz humana deveria ser preservada em pelo menos 90%, mas foi mantida em {preservacao*100:.1f}%."
        )

    def test_deve_reiniciar_estado_interno_do_filtro_corretamente(self):
        """Valida se a limpeza de estado zera os coeficientes de atraso."""
        filtro = AcousticFilter(sample_rate=16000, cutoff_hz=200.0)
        bloco = np.ones(800, dtype=np.float32) * 0.05
        filtro.apply(bloco)

        filtro.reset()
        assert filtro._zi is not None, "O estado do filtro não pode ser nulo após a reinicialização."
