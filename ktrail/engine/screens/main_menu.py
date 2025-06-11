from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGraphicsOpacityEffect, QStackedWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QParallelAnimationGroup, QPointF
from engine.rotating_panel import RotatingPanel


class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.background_pixmap = QPixmap("assets/textures/town.png")
        self.logo_pixmap = QPixmap("assets/textures/logo.png")
        self.b_x = 25
        self.b_y = 450
        self.logo_label = None
        self.background_label = QLabel(self)
        self.init_ui()
        self.init_intro()

    def paintEvent(self, event):
        if hasattr(self, "show_background") and self.show_background:
            super().paintEvent(event)
        # Фон рисуется через background_label

    def init_ui(self):
        self.setWindowTitle("Главное меню")
        self.setFixedSize(1920, 1080)

        # Устанавливаем фоновое изображение
        self.background_label = QLabel(self)
        if not self.background_pixmap.isNull():
            self.background_label.setPixmap(
                self.background_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            print("Ошибка: не удалось загрузить файл фона assets/textures/demo.png")

        # Градиент слева
        self.gradient_label = QLabel(self)
        self.gradient_label.setGeometry(0, 0, 800, 1080)
        self.gradient_label.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                 stop:0 rgba(0,0,0,250), stop:1 rgba(0,0,0,40));
        """)

        # Заголовок
        self.title_label = self.create_label("Ktrail", font_size=96, bold=True, x=225, y=220, w=600, h=150)

        # Кнопки
        self.start_button = self.create_button("Начать игру", self.start_game, x=self.b_x, y=self.b_y, w=750, h=55)
        self.start_duo_button = self.create_button("Играть вдвоем", self.start_duo, x=self.b_x, y=self.b_y + 80, w=750, h=55)
        self.settings_button = self.create_button("Настройки", self.open_settings, x=self.b_x, y=self.b_y + 160, w=750, h=55)
        self.exit_button = self.create_button("Выход", self.exit_game, x=self.b_x, y=self.b_y + 240, w=750, h=55)

        self.widgets_to_restore = [
            self.background_label,
            self.gradient_label,
            self.title_label,
            self.start_button,
            self.start_duo_button,
            self.settings_button,
            self.exit_button
        ]

        # Сохраняем оригинальные позиции
        for widget in self.widgets_to_restore:
            widget.setProperty("original_pos", widget.pos())
            widget.hide()

    def init_intro(self):
        """Показ логотипа перед меню"""
        self.logo_label = QLabel(self)
        if self.logo_pixmap.isNull():
            print("Ошибка: не удалось загрузить файл assets/textures/logo.png")
        else:
            self.logo_label.setPixmap(
                self.logo_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setGeometry(0, 0, self.width(), self.height())
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.show()
            self.fade(self.logo_label, duration=4000)

        QTimer.singleShot(4000, self.finish_intro)

    def finish_intro(self):
        """Завершение интро и показ меню"""
        self.show_background = True
        self.background_label.setPixmap(
            self.background_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.show()

        if self.logo_label:
            self.logo_label.hide()
            self.logo_label.deleteLater()
            self.logo_label = None

        for widget in [
            self.background_label,
            self.gradient_label,
            self.title_label,
            self.start_button,
            self.start_duo_button,
            self.settings_button,
            self.exit_button
        ]:
            widget.show()
            self.fade(widget, duration=600)

    def fade(self, widget, duration=500):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        animation.setStartValue(0)
        animation.setEndValue(1)
        widget.animation = animation
        animation.start()

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
                padding-left: 10px;
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

    def start_game(self):
        print("Переход к выбору дистанции...")
        self.disable_buttons()
        self.parent.distance_selection.is_duo = False
        self.animate_left_panel_out()

    def animate_left_panel_out(self):
        widgets_to_move = [
            self.gradient_label,
            self.title_label,
            self.start_button,
            self.start_duo_button,
            self.settings_button,
            self.exit_button
        ]

        for widget in widgets_to_move:
            anim = QPropertyAnimation(widget, b"pos")
            anim.setDuration(800)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setStartValue(widget.pos())
            anim.setEndValue(QPointF(-widget.width() - 50, widget.y()))
            anim.start()
            widget.anim = anim

        QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
        QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.distance_selection))

    def restore_positions(self):
        self.gradient_label.move(0, 0)
        self.title_label.move(225, 220)
        b_x = 25
        b_y = 450
        self.start_button.move(b_x, b_y)
        self.start_duo_button.move(b_x, b_y + 80)
        self.settings_button.move(b_x, b_y + 160)
        self.exit_button.move(b_x, b_y + 240)

        screen_pixmap = self.grab()

        RotatingPanel.assemble_transition(
            self,
            on_finished=self.enable_buttons,
            background_path=screen_pixmap  # Передаём pixmap напрямую
        )



    def start_duo(self):
        print("Переход к дуо...")
        self.disable_buttons()
        self.animate_left_panel_out()
        self.parent.distance_selection.is_duo = True

    def open_settings(self):
        print("Открытие настроек...")
        if self.parent:
            self.parent.settings_menu.set_previous_screen("main_menu")
            self.parent.setCurrentWidget(self.parent.settings_menu)

    def exit_game(self):
        print("Выход из игры...")
        if self.parent:
            self.parent.exit_game()

    def disable_buttons(self):
        for btn in [self.start_button, self.start_duo_button, self.settings_button, self.exit_button]:
            btn.setDisabled(True)

    def enable_buttons(self):
        for btn in [self.start_button, self.start_duo_button, self.settings_button, self.exit_button]:
            btn.setDisabled(False)
