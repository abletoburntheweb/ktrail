# engine/screens/pause_menu.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PauseMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Пауза")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Пауза")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        continue_button = QPushButton("Продолжить")
        continue_button.setFont(QFont("Arial", 18))
        continue_button.clicked.connect(self.continue_game)
        layout.addWidget(continue_button)

        settings_button = QPushButton("Настройки")
        settings_button.setFont(QFont("Arial", 18))
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)

        exit_to_main_menu_button = QPushButton("Выйти в главное меню")
        exit_to_main_menu_button.setFont(QFont("Arial", 18))
        exit_to_main_menu_button.clicked.connect(self.exit_to_main_menu)
        layout.addWidget(exit_to_main_menu_button)

        self.setLayout(layout)

    def continue_game(self):
        """Продолжить игру."""
        print("Продолжение игры...")
        if self.parent and hasattr(self.parent.game_screen, "toggle_pause"):
            self.parent.game_screen.toggle_pause()
            self.parent.setCurrentWidget(self.parent.game_screen)

    def open_settings(self):
        """Открыть меню настроек."""
        print("Открытие меню настроек...")
        if self.parent:
            self.parent.settings_menu.set_previous_screen("pause_menu")
            self.parent.setCurrentWidget(self.parent.settings_menu)

    def exit_to_main_menu(self):
        """Выйти в главное меню."""
        print("Выход в главное меню...")
        if self.parent and hasattr(self.parent.game_screen, "toggle_pause"):
            self.parent.game_screen.toggle_pause()
            self.parent.setCurrentWidget(self.parent.main_menu)