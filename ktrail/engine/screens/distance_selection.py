# engine/screens/distance_selection.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from engine.rotating_panel import RotatingPanel


class DistanceSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_duo = False
        self.background_pieces = []  # Хранение анимационных панелей
        self.background_pixmap = QPixmap("assets/textures/demo.png")  # Общее фоновое изображение
        self.layout_widgets = []  # Для временного хранения виджетов
        self.init_ui()
        self.hide_all_widgets()  # Скрываем всё при инициализации

    def init_ui(self):
        self.setWindowTitle("Выбор дистанции")
        self.setFixedSize(1920, 1080)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        title_label = QLabel("Выберите дистанцию:")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        self.layout_widgets.append(title_label)

        distances = [200, 500, 1000]
        for distance in distances:
            button = QPushButton(f"{distance} м")
            button.setFont(QFont("Arial", 24))
            button.clicked.connect(lambda _, d=distance: self.start_game(d))
            self.layout.addWidget(button)
            self.layout_widgets.append(button)

        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.go_back_with_animation)
        self.layout.addWidget(back_button)
        self.layout_widgets.append(back_button)

    def show_all_widgets(self):
        """Показывает все элементы интерфейса"""
        for widget in self.layout_widgets:
            widget.show()

    def hide_all_widgets(self):
        """Скрывает все элементы интерфейса"""
        for widget in self.layout_widgets:
            widget.hide()

    def disassemble_background(self):
        """Анимация разборки экрана перед выходом"""
        cols = 10
        rows = 6
        panel_w = self.width() // cols
        panel_h = self.height() // rows

        # Скрываем текущие виджеты
        self.hide_all_widgets()

        # Создаём квадратики на основе текущего фона
        for row in range(rows):
            for col in range(cols):
                piece = RotatingPanel(
                    parent=self,
                    pixmap=self.background_pixmap.copy(col * panel_w, row * panel_h, panel_w, panel_h),
                    x=col * panel_w,
                    y=row * panel_h,
                    width=panel_w,
                    height=panel_h
                )
                self.background_pieces.append(piece)
                piece.show()
                delay = (row + col) * 80
                QTimer.singleShot(delay, piece.assemble_animation)

        QTimer.singleShot(2000, self.finish_appearance)

    def finish_appearance(self):
        """Убираем квадратики и показываем основной интерфейс"""
        for piece in self.background_pieces:
            piece.hide()
            piece.deleteLater()
        self.background_pieces.clear()

        if hasattr(self, 'background_label'):
            self.background_label.deleteLater()
            del self.background_label

        self.show_all_widgets()  # Показываем кнопки и заголовок

    def start_game(self, distance):
        if self.parent:
            if self.is_duo == False:
                self.parent.game_screen.reset_game()
                self.parent.game_screen.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen)
            else:
                self.parent.game_screen_duo.reset_game()
                self.parent.game_screen_duo.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen_duo)

            self.is_duo = False

    def go_back(self):
        if self.parent:
            self.parent.main_menu.restore_menu()
            self.parent.setCurrentWidget(self.parent.main_menu)

    def go_back_with_animation(self):
        self.assemble_background()

    def assemble_background(self):
        """Анимация разборки экрана перед выходом"""
        cols = 10
        rows = 6
        panel_w = self.width() // cols
        panel_h = self.height() // rows

        # Скрываем текущие виджеты
        self.hide_all_widgets()

        # Создаём квадратики на основе текущего фона
        for row in range(rows):
            for col in range(cols):
                piece = RotatingPanel(
                    parent=self,
                    pixmap=self.background_pixmap.copy(col * panel_w, row * panel_h, panel_w, panel_h),
                    x=col * panel_w,
                    y=row * panel_h,
                    width=panel_w,
                    height=panel_h
                )
                self.background_pieces.append(piece)
                piece.show()
                delay = (row + col) * 80
                QTimer.singleShot(delay, piece.start_animation)

        QTimer.singleShot(2000, self.finish_transition)

    def finish_transition(self):
        """Очистка квадратиков и переход обратно"""
        for piece in self.background_pieces:
            piece.hide()
            piece.deleteLater()
        self.background_pieces.clear()

        if hasattr(self, 'background_label'):
            self.background_label.deleteLater()
            del self.background_label

        if self.parent:
            self.parent.main_menu.restore_menu()
            self.parent.setCurrentWidget(self.parent.main_menu)