"""
Componente visualizador de ondas sonoras em barras animadas.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QWidget

from src.ui.styles.theme import (
    COLOR_DIRECT_MODE,
    WAVEFORM_BAR_WIDTH,
    WAVEFORM_BAR_SPACING,
    WAVEFORM_BAR_COUNT,
    WAVEFORM_MIN_HEIGHT,
    WAVEFORM_MAX_HEIGHT
)


class AudioWaveformWidget(QWidget):
    """Visualizador reativo de volume do microfone com interpolação a 60fps."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(54, 24)
        self.amplitude = 0.0
        self.target_heights = [float(WAVEFORM_MIN_HEIGHT)] * WAVEFORM_BAR_COUNT
        self.current_heights = [float(WAVEFORM_MIN_HEIGHT)] * WAVEFORM_BAR_COUNT
        self.bar_color = COLOR_DIRECT_MODE

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_bars)
        self.timer.start(16)

    def set_amplitude(self, amp: float):
        """Atualiza a meta de altura das barras baseado no volume recebido."""
        self.amplitude = max(0.0, min(1.0, amp))
        multipliers = [0.7, 1.2, 1.5, 1.1, 0.8]
        for i in range(WAVEFORM_BAR_COUNT):
            h = WAVEFORM_MIN_HEIGHT + (self.amplitude * (WAVEFORM_MAX_HEIGHT - WAVEFORM_MIN_HEIGHT) * multipliers[i])
            self.target_heights[i] = min(float(WAVEFORM_MAX_HEIGHT), max(float(WAVEFORM_MIN_HEIGHT), h))

    def set_color(self, color: QColor):
        """Atualiza a cor das barras."""
        self.bar_color = color
        self.update()

    def _animate_bars(self):
        changed = False
        for i in range(WAVEFORM_BAR_COUNT):
            diff = self.target_heights[i] - self.current_heights[i]
            if abs(diff) > 0.1:
                self.current_heights[i] += diff * 0.25
                changed = True
        if changed:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        total_width = (WAVEFORM_BAR_COUNT * WAVEFORM_BAR_WIDTH) + ((WAVEFORM_BAR_COUNT - 1) * WAVEFORM_BAR_SPACING)
        start_x = (self.width() - total_width) / 2
        center_y = self.height() / 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.bar_color))

        for i in range(WAVEFORM_BAR_COUNT):
            h = self.current_heights[i]
            x = start_x + (i * (WAVEFORM_BAR_WIDTH + WAVEFORM_BAR_SPACING))
            y = center_y - (h / 2)
            painter.drawRoundedRect(int(x), int(y), int(WAVEFORM_BAR_WIDTH), int(h), 2, 2)
