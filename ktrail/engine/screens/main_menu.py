# engine/screens/main_menu.py
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt


class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.background_pixmap = QPixmap("assets/textures/demo.png")
        self.init_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        super().paintEvent(event)

    def init_ui(self):
        self.setWindowTitle("Главное меню")
        self.setFixedSize(1920, 1080)

        self.gradient_label = QLabel(self)
        self.gradient_label.setGeometry(0, 0, 1000, 1080)  # совпадает с областью меню
        self.gradient_label.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                 stop:0 rgba(0,0,0,220), stop:1 transparent);
        """)

        self.title_label = self.create_label("Ktrail", font_size=96, bold=True, x=150, y=100, w=600, h=150)

        self.start_button = self.create_button("Начать игру", self.start_game, x=125, y=420, w=550, h=55)
        self.start_duo_button = self.create_button("Играть вдвоем", self.start_duo, x=125, y=500, w=550, h=55)
        self.settings_button = self.create_button("Настройки", self.open_settings, x=125, y=580, w=550, h=55)
        self.exit_button = self.create_button("Выход", self.exit_game, x=125, y=660, w=550, h=55)

    def create_button(self, text, callback, x, y, w, h):
        button = QPushButton(text, self)
        button.setFont(QFont("Arial", 20))
        button.clicked.connect(callback)
        button.setGeometry(x, y, w, h)
        button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                 stop:0 black, stop:1 transparent);
                color: white;
                border: none;
                padding: 10px;
                font-size: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                 stop:0 darkgray, stop:1 transparent);
            }
        """)
        return button

    def create_label(self, text, font_size=18, bold=False, x=0, y=0, w=200, h=50):
        label = QLabel(text, self)
        font = QFont("Arial", font_size)
        if bold:
            font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setGeometry(x, y, w, h)
        return label

    # === Обработчики событий ===
    def start_game(self):
        print("Переход к выбору дистанции...")
        if self.parent:
            self.parent.distance_selection.is_duo = False
            print(f"Флаг is_duo установлен в {self.parent.distance_selection.is_duo}")
            self.parent.setCurrentWidget(self.parent.distance_selection)

    def start_duo(self):
        print("Переход к дуо...")
        if self.parent:
            self.parent.distance_selection.is_duo = True
            print(f"Флаг is_duo установлен в {self.parent.distance_selection.is_duo}")
            self.parent.setCurrentWidget(self.parent.distance_selection)

    def open_settings(self):
        print("Открытие настроек...")
        if self.parent:
            self.parent.settings_menu.set_previous_screen("main_menu")
            self.parent.setCurrentWidget(self.parent.settings_menu)

    def exit_game(self):
        print("Выход из игры...")
        if self.parent:
            self.parent.exit_game()