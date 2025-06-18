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
        self.previous_screen = None  # Атрибут для хранения предыдущего экрана
        self.overlay = None  # Прозрачный слой для модального окна
        self.leaderboard_widget = None  # Виджет таблицы рекордов
        self.is_first_init = True  # Флаг первой инициализации
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Заголовок
        title_label = QLabel("Таблица рекордов")
        title_label.setFont(QFont("Montserrat", 36, QFont.Bold))
        title_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(title_label)

        # Выпадающий список для выбора дистанции
        self.distance_combo = QComboBox()
        self.distance_combo.setFont(QFont("Montserrat", 18))
        self.distance_combo.addItem("")  # Пустой элемент по умолчанию
        self.distance_combo.addItems(["200 м", "500 м", "1000 м", "2000 м"])
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

        # Создаем стек виджетов для заглушки и таблицы
        self.stack = QStackedWidget()

        # Виджет заглушки
        self.placeholder = QLabel("Выберите дистанцию")
        self.placeholder.setFont(QFont("Montserrat", 24))
        self.placeholder.setStyleSheet("color: white; background-color: transparent;")
        self.placeholder.setAlignment(Qt.AlignCenter)

        # Таблица рекордов
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(3)  # Три колонки: "Место", "Имя", "Время"
        self.leaderboard_table.setHorizontalHeaderLabels(["Место", "Имя", "Время"])
        self.leaderboard_table.setRowCount(0)
        self.leaderboard_table.setFont(QFont("Montserrat", 16))
        self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
        self.leaderboard_table.verticalHeader().setVisible(False)  # Скрываем вертикальные заголовки

        # Отключаем выделение ячеек
        self.leaderboard_table.setSelectionMode(QTableWidget.NoSelection)

        # Настройка ширины столбцов
        self.leaderboard_table.setColumnWidth(0, 100)  # Ширина первого столбца ("Место")
        self.leaderboard_table.setColumnWidth(1, 200)  # Ширина второго столбца ("Имя")
        self.leaderboard_table.setColumnWidth(2, 200)  # Ширина третьего столбца ("Время")

        # Настройка скроллбара
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

        # Стилизация таблицы
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

        # Добавляем виджеты в стек
        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(self.leaderboard_table)
        self.stack.setCurrentWidget(self.placeholder)  # Показываем заглушку по умолчанию
        layout.addWidget(self.stack)

        # Кнопка "Закрыть"
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

    def open_leaderboard(self):
        """Открытие экрана рекордов как модального окна."""
        print("Открытие таблицы рекордов...")
        if self.parent:
            self.parent.play_select_sound()  # Воспроизведение звука select_click

        # Создаем прозрачный слой, который покрывает только правую часть экрана
        if not self.overlay:
            self.overlay = QWidget(self.parent)  # Overlay привязывается к родительскому виджету
            self.overlay.setGeometry(800, 0, 1120, 1080)  # Правая часть экрана (1920 - 800 = 1120)
            self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")  # Полупрозрачный фон
            self.overlay.hide()

        # Создаем виджет таблицы рекордов
        if not self.leaderboard_widget:
            self.leaderboard_widget = QWidget(self.overlay)  # Размещаем виджет на overlay
            self.leaderboard_widget.setFixedSize(1020, 600)  # Размер виджета
            self.leaderboard_widget.move(50, 240)  # Центрируем по вертикали и горизонтали
            self.leaderboard_widget.setStyleSheet("""
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
            """)
            self.init_ui()  # Инициализация интерфейса внутри виджета

        # При первом открытии сбрасываем выбор дистанции
        if self.is_first_init:
            self.distance_combo.setCurrentIndex(0)  # Выбираем пустой элемент
            self.stack.setCurrentWidget(self.placeholder)  # Показываем заглушку
            self.is_first_init = False

        # Показываем overlay и виджет рекордов
        self.overlay.show()
        self.fade(self.leaderboard_widget, duration=600)

    def close_leaderboard(self):
        """Закрытие экрана рекордов."""
        if self.parent:
            self.parent.main_menu.close_leaderboard()
            self.parent.play_cancel_sound()

    def fade(self, widget, duration=500, hide_after=False):
        """Анимация плавного появления/исчезновения виджета."""
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
        """Устанавливает предыдущий экран."""
        self.previous_screen = screen_name

    def update_leaderboard(self):
        """Обновление таблицы рекордов на основе выбранной дистанции."""
        if self.distance_combo.currentIndex() == 0:  # Если выбран пустой элемент
            self.stack.setCurrentWidget(self.placeholder)
            return

        selected_distance = self.distance_combo.currentText()  # Например, "200 м"
        distance = int(selected_distance.split()[0])  # Извлекаем число (например, 200)

        # Получаем данные из файла рекордов
        records = self.load_records(distance)

        # Очищаем таблицу
        self.leaderboard_table.setRowCount(0)

        # Заполняем таблицу данными
        for i, record in enumerate(records):
            self.leaderboard_table.insertRow(i)  # Добавляем строку
            place_item = QTableWidgetItem(str(i + 1))  # Место
            name_item = QTableWidgetItem(record["name"])  # Имя
            time_item = QTableWidgetItem(f"{record['time']:.2f} сек")  # Время

            # Отключаем возможность редактирования
            place_item.setFlags(place_item.flags() & ~Qt.ItemIsEditable)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)

            # Подсветка первых трех мест
            if i == 0:  # Золото
                place_item.setBackground(QColor(255, 215, 0, 100))  # Золотая подсветка
                name_item.setBackground(QColor(255, 215, 0, 100))
                time_item.setBackground(QColor(255, 215, 0, 100))
            elif i == 1:  # Серебро
                place_item.setBackground(QColor(192, 192, 192, 100))  # Серебряная подсветка
                name_item.setBackground(QColor(192, 192, 192, 100))
                time_item.setBackground(QColor(192, 192, 192, 100))
            elif i == 2:  # Бронза
                place_item.setBackground(QColor(205, 127, 50, 100))  # Бронзовая подсветка
                name_item.setBackground(QColor(205, 127, 50, 100))
                time_item.setBackground(QColor(205, 127, 50, 100))

            # Устанавливаем элементы в таблицу
            self.leaderboard_table.setItem(i, 0, place_item)  # Место
            self.leaderboard_table.setItem(i, 1, name_item)  # Имя
            self.leaderboard_table.setItem(i, 2, time_item)  # Время

        # Прокручиваем таблицу до начала
        self.leaderboard_table.scrollToTop()

        # Переключаем на таблицу
        self.stack.setCurrentWidget(self.leaderboard_table)

    def load_records(self, distance):
        """
        Загрузка рекордов для указанной дистанции.
        :param distance: Дистанция (в метрах).
        :return: Список записей в порядке убывания (лучшее время сверху).
        """
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        records = data.get(str(distance), [])
        # Сортируем записи по времени (по возрастанию)
        sorted_records = sorted(records, key=lambda x: x["time"])[:15]  # Ограничиваем до 15 лучших
        return sorted_records

    def save_record(self, distance, name, time):
        """
        Сохранение нового рекорда в файл.
        :param distance: Дистанция (в метрах).
        :param name: Имя игрока.
        :param time: Время (в секундах).
        """
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        # Получаем текущие записи для дистанции
        records = data.get(str(distance), [])

        # Добавляем новый рекорд
        records.append({"name": name, "time": time})

        # Сортируем записи по времени (по возрастанию)
        sorted_records = sorted(records, key=lambda x: x["time"])[:15]  # Ограничиваем до 15 лучших

        # Обновляем данные
        data[str(distance)] = sorted_records

        # Сохраняем обратно в файл
        with open("config/leaderboard.json", "w") as file:
            json.dump(data, file, indent=4)