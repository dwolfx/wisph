"""
Filtros acústicos para processamento de áudio.
Implementa filtro passa-alta Butterworth para eliminação de ruídos graves (trânsito, ventiladores).
"""

import numpy as np
from scipy import signal


class AcousticFilter:
    """Filtro passa-alta para atenuar frequências abaixo do ponto de corte."""
    
    def __init__(self, sample_rate: int = 16000, cutoff_hz: float = 200.0, order: int = 4):
        self.sample_rate = sample_rate
        self.cutoff_hz = cutoff_hz
        self.order = order
        
        nyquist = self.sample_rate / 2.0
        normalized_cutoff = self.cutoff_hz / nyquist
        self.b, self.a = signal.butter(self.order, normalized_cutoff, btype="high")
        self._zi = signal.lfilter_zi(self.b, self.a)

    def reset(self):
        """Reinicia o estado interno do filtro."""
        self._zi = signal.lfilter_zi(self.b, self.a)

    def apply(self, audio_data: np.ndarray) -> np.ndarray:
        """Aplica o filtro no bloco de áudio mantendo continuidade de estado."""
        filtered, self._zi = signal.lfilter(self.b, self.a, audio_data, zi=self._zi)
        return filtered
