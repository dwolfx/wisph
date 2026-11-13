"""
Configuração do pytest e fixtures reutilizáveis em Português (PT-BR).
"""

import sys
import os
import pytest
import numpy as np

# Adiciona a raiz do projeto ao sys.path para garantir importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def amostra_audio_ronco_carro():
    """Gera 1 segundo de sinal grave simulando ronco de escapamento (80 Hz)."""
    taxa = 16000
    tempo = np.linspace(0, 1.0, taxa, endpoint=False)
    sinal = 0.05 * np.sin(2 * np.pi * 80 * tempo)
    return sinal.astype(np.float32)


@pytest.fixture
def amostra_audio_voz_humana():
    """Gera 1 segundo de sinal na faixa da voz humana falada (450 Hz)."""
    taxa = 16000
    tempo = np.linspace(0, 1.0, taxa, endpoint=False)
    sinal = 0.03 * np.sin(2 * np.pi * 450 * tempo)
    return sinal.astype(np.float32)


@pytest.fixture
def amostra_clique_teclado():
    """Gera pulso curto simulando estalo de tecla mecânica (25ms)."""
    taxa = 16000
    tamanho_bloco = int(taxa * 0.05)  # Bloco de 50ms
    clique = np.zeros(tamanho_bloco, dtype=np.float32)
    clique[:int(taxa * 0.025)] = 0.04  # 25ms ativo
    return clique
