import json
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QLabel, \
    QGraphicsOpacityEffect, QStackedWidget
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve


class LeaderboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.previous_screen = None
        self.overlay = None
        self.leaderboard_widget = None
        self.is_first_init = True

        self.custom_distance_names = {
            " ": " ",
            "25000": "Лянгасово",
            "30000": "Сосновка",
            "45000": "Мухино",
            "58000": "Сулово"
        }
        self.initialize_distances()

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Таблица рекордов")
        title_label.setFont(QFont("Montserrat", 36, QFont.Bold))
        title_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(title_label)

        self.distance_combo = QComboBox()
        self.distance_combo.setFont(QFont("Montserrat", 18))

        for distance, custom_name in self.custom_distance_names.items():
            self.distance_combo.addItem(custom_name)
        self.distance_combo.currentIndexChanged.connect(self.update_leaderboard)
        self.distance_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: rgba(255, 255, 255, 20);
                border: 2px solid white;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                width: 30px;
                border-left: 2px solid white;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/arrow_down.png); /* Замените на путь к вашей иконке */
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                selection-background-color: rgba(255, 255, 255, 40);
                selection-color: white;
            }
        """)
        layout.addWidget(self.distance_combo)

        self.stack = QStackedWidget()

        self.placeholder = QLabel("Выберите дистанцию")
        self.placeholder.setFont(QFont("Montserrat", 24))
        self.placeholder.setStyleSheet("color: white; background-color: transparent;")
        self.placeholder.setAlignment(Qt.AlignCenter)

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Место", "Имя", "Время"])
        self.leaderboard_table.setRowCount(0)
        self.leaderboard_table.setFont(QFont("Montserrat", 16))
        self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
        self.leaderboard_table.verticalHeader().setVisible(False)

        self.leaderboard_table.setSelectionMode(QTableWidget.NoSelection)

        self.leaderboard_table.setColumnWidth(0, 100)
        self.leaderboard_table.setColumnWidth(1, 200)
        self.leaderboard_table.setColumnWidth(2, 200)

        self.leaderboard_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.leaderboard_table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 50);
                width: 15px;
                margin: 15px 0 15px 0;
                border: none;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 20);
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
        """)

        self.leaderboard_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: none;
                gridline-color: rgba(255, 255, 255, 40); /* Линии между ячейками */
            }
            QHeaderView::section {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 rgba(255, 255, 255, 20),
                                                  stop:1 rgba(255, 255, 255, 10));
                color: white;
                border: 1px solid rgba(255, 255, 255, 40);
                text-align: center;
                padding: 5px;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }
            QTableWidget::item {
                text-align: center;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: transparent; /* Отключаем подсветку при выборе */
            }
            QTableWidget::horizontalHeader {
                font-weight: bold;
            }
        """)

        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(self.leaderboard_table)
        self.stack.setCurrentWidget(self.placeholder)
        layout.addWidget(self.stack)

        close_button = QPushButton("Закрыть")
        close_button.setFont(QFont("Montserrat", 18))
        close_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(255, 255, 255, 20);
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
        """)
        close_button.clicked.connect(self.close_leaderboard)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def initialize_distances(self):
        all_distances = ["25000", "30000", "45000", "58000"]
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        for distance in all_distances:
            if distance not in data:
                data[distance] = []

        with open("config/leaderboard.json", "w") as file:
            json.dump(data, file, indent=4)

    def open_leaderboard(self):
        """Открытие экрана рекордов как модального окна."""
        print("Открытие таблицы рекордов...")
        if self.parent:
            self.parent.play_select_sound()

        if not self.overlay:
            self.overlay = QWidget(self.parent)
            self.overlay.setGeometry(800, 0, 1120, 1080)  # Правая часть экрана (1920 - 800 = 1120)
            self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
            self.overlay.hide()

        if not self.leaderboard_widget:
            self.leaderboard_widget = QWidget(self.overlay)
            self.leaderboard_widget.setFixedSize(1020, 600)  # Размер виджета
            self.leaderboard_widget.move(50, 240)  # Центрируем по вертикали и горизонтали
            self.leaderboard_widget.setStyleSheet("""
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
            """)
            self.init_ui()

        # При первом открытии сбрасываем выбор дистанции
        if self.is_first_init:
            self.distance_combo.setCurrentIndex(0)  # Выбираем пустой элемент
            self.stack.setCurrentWidget(self.placeholder)  # Показываем заглушку
            self.is_first_init = False

        self.overlay.show()
        self.fade(self.leaderboard_widget, duration=600)

    def close_leaderboard(self):
        if self.parent:
            self.parent.main_menu.close_leaderboard()
            self.parent.play_cancel_sound()

    def fade(self, widget, duration=500, hide_after=False):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        animation.setStartValue(1 if hide_after else 0)
        animation.setEndValue(0 if hide_after else 1)
        animation.start()
        if hide_after:
            animation.finished.connect(widget.hide)

    def set_previous_screen(self, screen_name):
        self.previous_screen = screen_name

    def update_leaderboard(self):
        """Обновление таблицы рекордов на основе выбранной дистанции."""
        selected_custom_name = self.distance_combo.currentText()
        if not selected_custom_name:
            self.stack.setCurrentWidget(self.placeholder)
            return

        distance = None
        for real_distance, custom_name in self.custom_distance_names.items():
            if custom_name == selected_custom_name:
                distance = int(real_distance)
                break

        if not distance:
            self.stack.setCurrentWidget(self.placeholder)
            return

        records = self.load_records(distance)

        self.leaderboard_table.setRowCount(0)

        for i, record in enumerate(records):
            self.leaderboard_table.insertRow(i)
            place_item = QTableWidgetItem(str(i + 1))
            name_item = QTableWidgetItem(record["name"])
            time_item = QTableWidgetItem(f"{record['time']:.2f} сек")

            place_item.setFlags(place_item.flags() & ~Qt.ItemIsEditable)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)

            # Подсветка первых трех мест
            if i == 0:  # Золото
                place_item.setBackground(QColor(255, 215, 0, 100))
                name_item.setBackground(QColor(255, 215, 0, 100))
                time_item.setBackground(QColor(255, 215, 0, 100))
            elif i == 1:  # Серебро
                place_item.setBackground(QColor(192, 192, 192, 100))
                name_item.setBackground(QColor(192, 192, 192, 100))
                time_item.setBackground(QColor(192, 192, 192, 100))
            elif i == 2:  # Бронза
                place_item.setBackground(QColor(205, 127, 50, 100))
                name_item.setBackground(QColor(205, 127, 50, 100))
                time_item.setBackground(QColor(205, 127, 50, 100))

            self.leaderboard_table.setItem(i, 0, place_item)
            self.leaderboard_table.setItem(i, 1, name_item)
            self.leaderboard_table.setItem(i, 2, time_item)

        self.leaderboard_table.scrollToTop()

        self.stack.setCurrentWidget(self.leaderboard_table)

    def load_records(self, distance):
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        records = data.get(str(distance), [])
        sorted_records = sorted(records, key=lambda x: x["time"])[:15]
        return sorted_records

    def save_record(self, distance, name, time):
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        records = data.get(str(distance), [])

        records.append({"name": name, "time": time})

        sorted_records = sorted(records, key=lambda x: x["time"])[:15]

        data[str(distance)] = sorted_records

        with open("config/leaderboard.json", "w") as file:
            json.dump(data, file, indent=4)