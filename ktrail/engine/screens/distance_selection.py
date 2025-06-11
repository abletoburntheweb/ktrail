# engine/screens/distance_selection.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from engine.rotating_panel import RotatingPanel  # <- убедись, что путь правильный


class DistanceSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_duo = False
        self.widgets_to_animate = []  # Для кнопок и заголовка
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Выбор дистанции")
        self.setFixedSize(1920, 1080)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.title_label = QLabel("Выберите дистанцию:")
        self.title_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.hide()
        self.layout.addWidget(self.title_label)
        self.widgets_to_animate.append(self.title_label)

        distances = [200, 500, 1000]
        self.distance_buttons = []
        for distance in distances:
            button = QPushButton(f"{distance} м")
            button.setFont(QFont("Arial", 24))
            button.clicked.connect(lambda _, d=distance: self.start_game(d))
            button.hide()
            self.layout.addWidget(button)
            self.distance_buttons.append(button)
            self.widgets_to_animate.append(button)

        self.back_button = QPushButton("Назад")
        self.back_button.setFont(QFont("Arial", 18))
        self.back_button.clicked.connect(self.go_back)
        self.back_button.hide()
        self.layout.addWidget(self.back_button)
        self.widgets_to_animate.append(self.back_button)

    def showEvent(self, event):
        """Вызывается при показе виджета"""
        super().showEvent(event)
        # Скрываем все элементы перед анимацией
        for widget in self.widgets_to_animate:
            widget.hide()
        # Запускаем анимацию сборки через RotatingPanel
        RotatingPanel.assemble_transition(
            self,
            on_finished=self.on_animation_finished,
            background_path="assets/textures/dev_car.png"
        )

    def on_animation_finished(self):
        self.temp_background = QLabel(self)
        dev_g_pixmap = QPixmap("assets/textures/dev_car.png")
        scaled = dev_g_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.temp_background.setPixmap(scaled)
        self.temp_background.resize(self.size())
        self.temp_background.move(0, 0)
        self.temp_background.show()
        self.temp_background.raise_()

        for widget in self.widgets_to_animate:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            widget.anim = anim
            anim.start()
            widget.show()

            widget.raise_()
            self.enable_buttons()

    def disable_buttons(self):
        for widget in self.widgets_to_animate:
            if isinstance(widget, QPushButton):
                widget.setDisabled(True)

    def enable_buttons(self):
        for widget in self.widgets_to_animate:
            if isinstance(widget, QPushButton):
                widget.setDisabled(False)

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
            self.disable_buttons()
            QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
            QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
            QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())
