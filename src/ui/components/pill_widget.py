"""
Widget Flutuante Translúcido (Floating Pill).
Apresenta o status de escuta, ondas sonoras e estados de transcrição.
"""

import os
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPainter, QLinearGradient, QPen, QBrush
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication

from src.ui.components.waveform import AudioWaveformWidget
from src.ui.styles.theme import (
    PILL_WIDTH,
    PILL_HEIGHT,
    PILL_BORDER_RADIUS,
    COLOR_BG_TOP,
    COLOR_BG_BOTTOM,
    COLOR_DIRECT_MODE,
    COLOR_SMART_MODE,
    COLOR_SUCCESS,
    COLOR_BORDER_DIRECT,
    COLOR_BORDER_SMART
)


class FloatingPill(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self.current_mode = "smart"
        self.current_state = "idle"
        self._drag_pos = QPoint()

        self._init_ui()
        self._load_stylesheet()
        self._center_top()

    def _init_ui(self):
        self.setFixedSize(PILL_WIDTH, PILL_HEIGHT)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 0, 16, 0)
        self.layout.setSpacing(10)

        self.status_icon = QLabel("🎙️", self)
        self.status_icon.setObjectName("statusIcon")
        self.layout.addWidget(self.status_icon)

        self.label_status = QLabel("Ouvindo...", self)
        self.label_status.setObjectName("statusLabel")
        self.layout.addWidget(self.label_status)

        self.layout.addStretch()

        self.waveform = AudioWaveformWidget(self)
        self.layout.addWidget(self.waveform)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def _load_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(__file__), "..", "styles", "pill.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _center_top(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 40
        self.move(x, y)

    def show_waiting(self, mode: str = "smart"):
        """Exibe o estado de escuta contínua Mãos-Livres."""
        self.hide_timer.stop()
        self.current_mode = mode
        self.current_state = "waiting"
        self.status_icon.setText("🎧")
        self.label_status.setText("Mãos-Livres (Aguardando fala...)")
        self.waveform.set_color(COLOR_SMART_MODE)
        self.waveform.set_amplitude(0.0)
        self.waveform.setVisible(True)
        self.show()
        self.update()

    def show_listening(self, mode: str = "direct"):
        """Exibe o estado de gravação de voz."""
        self.hide_timer.stop()
        self.current_mode = mode
        self.current_state = "listening"

        if mode == "smart":
            self.status_icon.setText("✨")
            self.label_status.setText("Modo Smart...")
            self.waveform.set_color(COLOR_SMART_MODE)
        else:
            self.status_icon.setText("🎙️")
            self.label_status.setText("Ouvindo...")
            self.waveform.set_color(COLOR_DIRECT_MODE)

        self.waveform.setVisible(True)
        self.show()
        self.update()

    def show_transcribing(self):
        self.current_state = "transcribing"
        self.status_icon.setText("⚡")
        self.label_status.setText("Transcrevendo...")
        self.update()

    def show_polishing(self):
        self.current_state = "polishing"
        self.status_icon.setText("🪄")
        self.label_status.setText("Refinando com IA...")
        self.waveform.set_color(COLOR_SUCCESS)
        self.update()

    def show_done(self, text_preview: str = "", auto_hide: bool = True):
        self.current_state = "done"
        self.status_icon.setText("✅")
        self.label_status.setText("Copiado!")
        self.waveform.setVisible(False)
        self.update()

        if auto_hide:
            self.hide_timer.start(1200)

    def set_amplitude(self, amp: float):
        if self.current_state in ["listening", "waiting"]:
            self.waveform.set_amplitude(amp)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        border_color = COLOR_BORDER_SMART if self.current_mode == "smart" else COLOR_BORDER_DIRECT

        bg_gradient = QLinearGradient(0, 0, 0, self.height())
        bg_gradient.setColorAt(0.0, COLOR_BG_TOP)
        bg_gradient.setColorAt(1.0, COLOR_BG_BOTTOM)

        painter.setBrush(QBrush(bg_gradient))
        painter.setPen(QPen(border_color, 1.2))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), PILL_BORDER_RADIUS, PILL_BORDER_RADIUS)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
