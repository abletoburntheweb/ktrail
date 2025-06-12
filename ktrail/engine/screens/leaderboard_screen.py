import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QLabel
from PyQt5.QtGui import QFont

class LeaderboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.previous_screen = None  # Атрибут для хранения предыдущего экрана
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Таблица рекордов")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Таблица рекордов")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Выпадающий список для выбора дистанции
        self.distance_combo = QComboBox()
        self.distance_combo.setFont(QFont("Arial", 18))
        self.distance_combo.addItems(["200 м", "500 м", "1000 м", "2000 м"])
        self.distance_combo.currentIndexChanged.connect(self.update_leaderboard)
        layout.addWidget(self.distance_combo)

        # Таблица рекордов
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(2)  # Две колонки: "Место" и "Время"
        self.leaderboard_table.setHorizontalHeaderLabels(["Место", "Время"])
        self.leaderboard_table.setRowCount(0)
        self.leaderboard_table.setFont(QFont("Arial", 16))
        self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.leaderboard_table)

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.return_to_previous_screen)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def set_previous_screen(self, screen_name):
        """Устанавливает предыдущий экран."""
        self.previous_screen = screen_name

    def return_to_previous_screen(self):
        """Возвращает пользователя на предыдущий экран."""
        if self.previous_screen == "pause_menu":
            print("Возвращение в меню паузы...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.pause_menu)
        elif self.previous_screen == "main_menu":
            print("Возвращение в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)
                self.parent.play_cancel_sound()
        else:
            print("Неизвестный предыдущий экран. Возвращаемся в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)

    def update_leaderboard(self):
        """Обновление таблицы рекордов на основе выбранной дистанции."""
        selected_distance = self.distance_combo.currentText()  # Например, "200 м"
        distance = int(selected_distance.split()[0])  # Извлекаем число (например, 200)

        # Получаем данные из файла рекордов
        records = self.load_records(distance)

        # Очищаем таблицу
        self.leaderboard_table.setRowCount(0)

        # Заполняем таблицу данными
        for i, time in enumerate(records):
            self.leaderboard_table.insertRow(i)
            self.leaderboard_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))  # Место
            self.leaderboard_table.setItem(i, 1, QTableWidgetItem(f"{time:.2f} сек"))  # Время

    def load_records(self, distance):
        """
        Загрузка рекордов для указанной дистанции.
        :param distance: Дистанция (в метрах).
        :return: Список времен в порядке убывания (лучшее время сверху).
        """
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        return sorted(data.get(str(distance), []))  # Сортируем по времени