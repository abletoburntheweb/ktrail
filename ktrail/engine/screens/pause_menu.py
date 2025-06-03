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

        exit_to_main_menu_button = QPushButton("Выйти в главное меню")
        exit_to_main_menu_button.setFont(QFont("Arial", 18))
        exit_to_main_menu_button.clicked.connect(self.exit_to_main_menu)
        layout.addWidget(exit_to_main_menu_button)

        # Установка макета
        self.setLayout(layout)

    def continue_game(self):
        """ Продолжить """
        print("Продолжение игры...")
        if self.parent:
            self.parent.setCurrentWidget(self.parent.game_screen)  # Возвращаемся к игровому экрану

    def exit_to_main_menu(self):
        """ Выйти в главное меню"""
        print("Выход в главное меню...")
        if self.parent:
            self.parent.setCurrentWidget(self.parent.main_menu)  # Возвращаемся к главному меню