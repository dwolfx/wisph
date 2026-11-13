"""
Módulo do ícone e menu do System Tray no Windows.
"""

import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt


def create_tray_icon_pixmap() -> QPixmap:
    """Gera um ícone vetorial limpo dinamicamente para o System Tray."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(139, 92, 246))
    painter.drawEllipse(2, 2, 28, 28)

    painter.setPen(QColor(255, 255, 255))
    font = QFont("Segoe UI", 13, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "W")
    painter.end()

    return pixmap


class SystemTray:
    def __init__(self, app, on_quit=None, on_model_changed=None, on_mode_changed=None, on_hands_free_toggled=None):
        self.app = app
        self.on_quit = on_quit
        self.on_model_changed = on_model_changed
        self.on_mode_changed = on_mode_changed
        self.on_hands_free_toggled = on_hands_free_toggled

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(create_tray_icon_pixmap()))
        self.tray_icon.setToolTip("OpenWhispr Windows (Voice Flow)")

        self._create_menu()
        self.tray_icon.show()

    def _create_menu(self):
        menu = QMenu()
        qss_path = os.path.join(os.path.dirname(__file__), "styles", "tray.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                menu.setStyleSheet(f.read())

        title_action = menu.addAction("🎙️ OpenWhispr Windows")
        title_action.setEnabled(False)

        menu.addSeparator()

        self.action_hands_free = menu.addAction("🎧 Modo Mãos-Livres (Sem Atalhos)")
        self.action_hands_free.setCheckable(True)
        self.action_hands_free.setChecked(False)

        def toggle_hf():
            if self.on_hands_free_toggled:
                self.on_hands_free_toggled(self.action_hands_free.isChecked())
        self.action_hands_free.triggered.connect(toggle_hf)

        menu.addSeparator()

        hk_direct = menu.addAction("Ditado Direto: Ctrl + Shift + Espaço")
        hk_direct.setEnabled(False)

        hk_smart = menu.addAction("Modo Smart (IA): Ctrl + Alt + Espaço")
        hk_smart.setEnabled(False)

        menu.addSeparator()

        # Seleção de Modelo
        model_menu = menu.addMenu("Modelo Whisper")
        models = [("tiny (Super Rápido)", "tiny"), ("base (Recomendado)", "base"), ("small (Maior Precisão)", "small")]
        for label, m_id in models:
            act = model_menu.addAction(label)
            act.setCheckable(True)
            if m_id == "base":
                act.setChecked(True)

            def make_handler(model_name=m_id, current_act=act):
                def handler():
                    for a in model_menu.actions():
                        a.setChecked(False)
                    current_act.setChecked(True)
                    if self.on_model_changed:
                        self.on_model_changed(model_name)
                return handler

            act.triggered.connect(make_handler(m_id, act))

        menu.addSeparator()

        quit_action = menu.addAction("Sair do OpenWhispr")
        quit_action.triggered.connect(self._handle_quit)

        self.tray_icon.setContextMenu(menu)

    def _handle_quit(self):
        if self.on_quit:
            self.on_quit()
        self.app.quit()
