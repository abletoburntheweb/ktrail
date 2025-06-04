# engine/screens/main_menu.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Главное меню")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("ktrail")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 18))
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button)

        settings_button = QPushButton("Настройки")
        settings_button.setFont(QFont("Arial", 18))
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)

        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont("Arial", 18))
        exit_button.clicked.connect(self.exit_game)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def start_game(self):
        """Начать игру."""
        print("Запуск игры...")
        if self.parent:
            self.parent.game_screen.reset_game()
            self.parent.game_screen.timer.start(16)
            self.parent.game_screen.obstacle_spawn_timer.start(2000)
            self.parent.setCurrentWidget(self.parent.game_screen)

    def open_settings(self):
        """Настройки"""
        print("Открытие настроек...")
        if self.parent:
            self.parent.settings_menu.set_previous_screen("main_menu")
            self.parent.setCurrentWidget(self.parent.settings_menu)

    def exit_game(self):
        """ Выход """
        print("Выход из игры...")
        if self.parent:
            self.parent.exit_game()