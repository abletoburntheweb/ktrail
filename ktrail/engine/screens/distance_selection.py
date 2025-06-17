from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QApplication
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class DistanceSelection(QWidget):
    def __init__(self, parent=None, is_duo=False, y_duo=568, y_single=390):
        super().__init__(parent)
        self.parent = parent
        self.is_duo = is_duo
        self.y_duo = y_duo
        self.y_single = y_single
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Выбор дистанции")
        self.setFixedSize(1920, 1080)

        # Определяем фон и список городов в зависимости от режима
        if self.is_duo:
            bg_image = "assets/textures/cus2.png"
            cities = [
                {"name": "Сосновка", "distance": 25000},
                {"name": "Матвеево", "distance": 30000},
                {"name": "Верхняя Тойма", "distance": 35000},
                {"name": "Нижняя Тойма", "distance": 38000}
            ]
            start_x = 416  # Начальная позиция по оси X для двойного режима
            start_y = self.y_duo
        else:
            bg_image = "assets/textures/cus.png"
            cities = [
                {"name": "Лянгасово", "distance": 25000},
                {"name": "Сосновка", "distance": 30000},
                {"name": "Мухино", "distance": 45000},
                {"name": "Сулово", "distance": 58000}
            ]
            start_x = 612  # Начальная позиция по оси X для одиночного режима
            start_y = self.y_single

        x_offset = 284  # Смещение между кнопками по оси X

        # Фоновая сетка
        self.grid_label = QLabel(self)
        self.grid_label.setPixmap(QPixmap(bg_image))
        self.grid_label.resize(self.size())
        self.grid_label.move(0, 0)
        self.grid_label.show()
        self.grid_label.raise_()

        for i, city in enumerate(cities):
            # Вычисляем позицию X для текущей кнопки
            current_x = start_x + i * (100 + x_offset)  # 100 — ширина кнопки, x_offset — дополнительное смещение

            # Создаем круглую кнопку (кружок)
            circle_button = QPushButton(city["name"], self)  # Указываем родительский виджет (self)
            circle_button.setFont(QFont("Arial", 18))
            circle_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(90, 75, 60, 102); /* Синий фон с 50% прозрачностью */
                    border-radius: 50%; /* Круглая форма */
                    padding: 20px;
                    color: white; /* Белый текст */
                }
                QPushButton:hover {
                    background-color: rgba(70, 60, 50, 140);  /* Темно-синий фон при наведении */
                }
            """)
            circle_button.setGeometry(current_x, start_y, 120, 120)
            circle_button.clicked.connect(lambda _, d=city["distance"]: self.start_game(d))

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад", self)  # Указываем родительский виджет (self)
        self.back_button.setFont(QFont("Arial", 18))
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setGeometry(300, 200, 200, 50)  # Устанавливаем размер и позицию

    def reset_ui(self):
        # Очищаем старые виджеты
        for child in self.children():
            if isinstance(child, QPushButton) and child != self.back_button:
                child.deleteLater()

        # Переинициализируем UI с текущим режимом (is_duo)
        self.init_ui()
    def start_game(self, distance):
        if self.parent:
            if not self.is_duo:
                self.parent.game_screen.reset_game()
                self.parent.game_screen.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen)
            else:
                self.parent.game_screen_duo.reset_game()
                self.parent.game_screen_duo.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen_duo)

    def go_back(self):
        if self.parent:
            self.parent.play_cancel_sound()
            self.parent.setCurrentWidget(self.parent.main_menu)