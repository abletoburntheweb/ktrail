from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont, QPainter
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPointF

from engine.screens.settings_menu import SettingsMenu


class PauseMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.background_pixmap = QPixmap("assets/textures/town.png")  # Фоновое изображение
        self.b_x = 25  # Начальная координата X для кнопок
        self.b_y = 450  # Начальная координата Y для кнопок
        self.overlay = None  # Прозрачный слой для модального окна
        self.settings_menu = None  # Виджет настроек
        self.is_settings_open = False  # Флаг состояния настроек
        self.last_frame_pixmap = None
        self.init_ui()

    def set_last_frame(self, pixmap):
        """Установка последнего кадра игры."""
        self.last_frame_pixmap = pixmap
        self.update()  # Обновляем виджет, чтобы перерисовать фон

    def paintEvent(self, event):
        """Рисование фона."""
        painter = QPainter(self)
        if self.last_frame_pixmap:
            painter.drawPixmap(self.rect(), self.last_frame_pixmap)
        else:
            # Если кадр не захвачен, рисуем фон по умолчанию
            if not self.background_pixmap.isNull():
                painter.drawPixmap(self.rect(), self.background_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio,
                                                                              Qt.SmoothTransformation))

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Пауза")
        self.setFixedSize(1920, 1080)

        # Градиент слева
        self.gradient_label = QLabel(self)
        self.gradient_label.setGeometry(0, 0, 800, 1080)
        self.gradient_label.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 rgba(0,0,0,250), stop:1 rgba(0,0,0,40));
        """)

        # Заголовок
        self.title_label = self.create_label("Пауза", font_size=96, bold=True, x=225, y=220, w=600, h=150)

        # Кнопки
        self.continue_button = self.create_button("Продолжить", self.continue_game, x=self.b_x, y=self.b_y, w=750, h=55)
        self.settings_button = self.create_button("Настройки", self.open_settings, x=self.b_x, y=self.b_y + 80, w=750, h=55)
        self.exit_to_main_menu_button = self.create_button("Выйти в главное меню", self.exit_to_main_menu, x=self.b_x, y=self.b_y + 160, w=750, h=55)

        # Список виджетов для анимации
        self.widgets_to_restore = [
            self.gradient_label,
            self.title_label,
            self.continue_button,
            self.settings_button,
            self.exit_to_main_menu_button
        ]

        # Сохраняем оригинальные позиции
        for widget in self.widgets_to_restore:
            widget.setProperty("original_pos", widget.pos())
            widget.hide()

        # Показываем элементы с анимацией
        QTimer.singleShot(100, self.show_elements_with_animation)

    def show_elements_with_animation(self):
        """Показ элементов с анимацией."""
        self.show_background = True
        for widget in self.widgets_to_restore:
            widget.show()
            self.fade(widget, duration=600)

    def fade(self, widget, duration=500):
        """Анимация появления виджета."""
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
        """Создание кнопки."""
        button = QPushButton(text, self)
        button.setFont(QFont("Montserrat", 20))
        button.clicked.connect(lambda: self.play_button_sound_and_callback(callback))
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
        """Создание метки."""
        label = QLabel(text, self)
        font = QFont("Montserrat", font_size)
        if bold:
            font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setGeometry(x, y, w, h)
        return label

    def play_button_sound_and_callback(self, callback):
        """Воспроизведение звука кнопки и выполнение связанного действия."""
        if self.parent:
            if callback.__name__ == "exit_to_main_menu":
                self.parent.play_cancel_sound()  # Звук для кнопки "Выход"
            else:
                self.parent.play_select_sound()  # Звук по умолчанию
        callback()  # Выполнение связанного действия

    def continue_game(self):
        """Продолжить игру."""
        print("Продолжение игры...")
        if self.parent:
            if self.parent.main_menu.current_mode == "duo":
                if hasattr(self.parent.game_screen_duo, "toggle_pause"):
                    self.parent.game_screen_duo.toggle_pause()
                    self.parent.setCurrentWidget(self.parent.game_screen_duo)
            else:
                if hasattr(self.parent.game_screen, "toggle_pause"):
                    self.parent.game_screen.toggle_pause()
                    self.parent.setCurrentWidget(self.parent.game_screen)

    def open_settings(self):
        """Открыть или закрыть меню настроек."""
        print("Обработка настроек...")
        if self.is_settings_open:
            print("Настройки уже открыты. Закрываем их.")
            if self.parent:
                self.parent.play_cancel_sound()  # Воспроизведение звука cancel_click
            self.close_settings()
            return

        print("Открываем настройки...")
        if self.parent:
            self.parent.play_select_sound()  # Воспроизведение звука select_click

        # Создаем прозрачный слой, если его еще нет
        if not self.overlay:
            self.overlay = QWidget(self)
            self.overlay.setGeometry(800, 0, 1120, 1080)  # Правая часть экрана
            self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
            self.overlay.hide()

        # Создаем виджет настроек
        if not self.settings_menu:
            self.settings_menu = SettingsMenu(parent=self.parent)
            self.settings_menu.setParent(self.overlay)  # Размещаем настройки на overlay
            self.settings_menu.move(50, 240)  # Центрируем по вертикали и горизонтали
            self.settings_menu.setFixedSize(1020, 600)

        # Показываем overlay и настройки
        self.overlay.show()
        self.settings_menu.show()
        self.is_settings_open = True  # Устанавливаем флаг, что настройки открыты

    def close_settings(self):
        """Закрытие экрана настроек."""
        if self.settings_menu:
            self.settings_menu.hide()
        if self.overlay:
            self.overlay.hide()
        self.is_settings_open = False  # Сбрасываем флаг
        if self.parent:
            self.parent.play_cancel_sound()  # Воспроизводим звук cancel_click

    def exit_to_main_menu(self):
        """Выйти в главное меню."""
        print("Выход в главное меню...")
        if self.parent:
            self.parent.play_cancel_sound()  # Звуковой эффект cancel_click
        if self.parent and hasattr(self.parent.game_screen, "toggle_pause"):
            self.parent.game_screen.toggle_pause()
            self.parent.setCurrentWidget(self.parent.main_menu)