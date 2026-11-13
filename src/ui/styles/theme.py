"""
Central de design tokens e variáveis visuais do OpenWhispr Windows.
Altera cores, gradientes e dimensões em um único lugar.
"""

from PySide6.QtGui import QColor

# Dimensões da Interface
PILL_WIDTH = 320
PILL_HEIGHT = 48
PILL_BORDER_RADIUS = 22

# Paleta de Cores
COLOR_BG_TOP = QColor(22, 23, 29, 235)
COLOR_BG_BOTTOM = QColor(12, 13, 17, 248)

# Modos e Estados
COLOR_DIRECT_MODE = QColor(168, 85, 247)      # Roxo elétrico
COLOR_SMART_MODE = QColor(6, 182, 212)        # Ciano cibernético
COLOR_SUCCESS = QColor(16, 185, 129)          # Verde esmeralda
COLOR_BORDER_DIRECT = QColor(168, 85, 247, 160)
COLOR_BORDER_SMART = QColor(6, 182, 212, 160)

# Barras de Onda Sonora
WAVEFORM_BAR_WIDTH = 4
WAVEFORM_BAR_SPACING = 5
WAVEFORM_BAR_COUNT = 5
WAVEFORM_MIN_HEIGHT = 4
WAVEFORM_MAX_HEIGHT = 20
