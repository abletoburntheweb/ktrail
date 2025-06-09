# engine/screens/distance_selection.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class DistanceSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Выбор дистанции")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Выберите дистанцию:")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        distances = [200, 500, 1000]
        for distance in distances:
            button = QPushButton(f"{distance} м")
            button.setFont(QFont("Arial", 24))
            button.clicked.connect(lambda _, d=distance: self.start_game(d))
            layout.addWidget(button)

        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def start_game(self, distance):
        """Передаём выбранную дистанцию в GameScreen и запускаем игру"""
        if self.parent:
            self.parent.game_screen.reset_game()
            self.parent.game_screen.set_target_distance(distance)
            self.parent.setCurrentWidget(self.parent.game_screen)

    def go_back(self):
        """Возвращаемся в главное меню"""
        if self.parent:
            self.parent.setCurrentWidget(self.parent.main_menu)