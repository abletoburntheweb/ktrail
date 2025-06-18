import json

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGraphicsOpacityEffect, QStackedWidget, QLineEdit
from PyQt5.QtGui import QPixmap, QFont, QRegExpValidator
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QParallelAnimationGroup, QPointF, QRegExp
from engine.rotating_panel import RotatingPanel
from engine.screens.leaderboard_screen import LeaderboardScreen
from engine.screens.settings_menu import SettingsMenu


class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.overlay = None  # Прозрачный слой для модального окна
        self.settings_menu = None  # Виджет настроек
        self.leaderboard_widget = None  # Виджет таблицы рекордов
        self.current_modal_widget = None
        self.is_leaderboard_open = False  # Флаг состояния таблицы рекордов
        self.is_settings_open = False  # Флаг состояния настроек
        self.current_mode = None
        self.background_pixmap = QPixmap("assets/textures/town.png")
        self.logo_pixmap = QPixmap("assets/textures/logo2.png")
        self.b_x = 25
        self.b_y = 450
        self.logo_label = None
        self.background_label = QLabel(self)
        self.is_intro_finished = False  # Флаг завершения интро
        self.init_ui()
        self.init_intro()

        # Загрузка имени пользователя из leaderboard.json
        self.load_username()

        # Добавляем QLabel для отображения имени пользователя
        self.username_label = QLabel(self.username, self)
        self.username_label.setFont(QFont("Montserrat", 24))
        self.username_label.setStyleSheet("color: white;")
        self.username_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.username_label.setGeometry(self.width() - 200, self.height() - 50, 180, 40)
        self.username_label.setCursor(Qt.PointingHandCursor)  # Меняем курсор при наведении
        self.username_label.mousePressEvent = self.edit_username  # Обработчик клика

        # Добавляем QLineEdit для редактирования имени
        self.username_edit = QLineEdit(self)
        self.username_edit.setFixedSize(180, 40)
        self.username_edit.setFont(QFont("Montserrat", 24))
        self.username_edit.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.username_edit.setMaxLength(3)  # Ограничение в 3 символа
        regex = QRegExp("[A-Z]{1,3}")  # Только заглавные латинские буквы
        validator = QRegExpValidator(regex, self)
        self.username_edit.setValidator(validator)
        self.username_edit.returnPressed.connect(self.save_username)  # Сохранение при нажатии Enter

        # Устанавливаем стиль для QLineEdit
        self.username_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.8);
                border-radius: 8px;
                color: white;
                font-size: 24px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 255, 0.8);
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)

        # Добавляем плейсхолдер
        self.username_edit.setPlaceholderText("ABC")  # Плейсхолдер с примером
        self.username_edit.textChanged.connect(self.validate_username)
        self.username_edit.hide()  # Скрываем поле редактирования изначально

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
        self.title_label = self.create_label("|Ktrail", font_size=96, bold=True, x=0, y=220, w=750, h=150)

        # Кнопки
        self.start_button = self.create_button("Начать игру", self.start_game, x=self.b_x, y=self.b_y, w=750, h=55)
        self.start_duo_button = self.create_button("Играть вдвоем", self.start_duo, x=self.b_x, y=self.b_y + 80, w=750, h=55)
        self.leaderboard_button = self.create_button("Таблица рекордов", self.open_leaderboard, x=self.b_x, y=self.b_y + 160, w=550, h=55
        )
        self.settings_button = self.create_button("Настройки", self.open_settings, x=self.b_x, y=self.b_y + 240, w=750, h=55)
        self.exit_button = self.create_button("Выход", self.exit_game, x=self.b_x, y=self.b_y + 320, w=750, h=55)

        self.widgets_to_restore = [
            self.background_label,
            self.gradient_label,
            self.title_label,
            self.start_button,
            self.start_duo_button,
            self.leaderboard_button,
            self.settings_button,
            self.exit_button
        ]

        # Сохраняем оригинальные позиции
        for widget in self.widgets_to_restore:
            widget.setProperty("original_pos", widget.pos())
            widget.hide()

    def init_intro(self):
        """Показ логотипа перед меню."""
        self.logo_label = QLabel(self)
        if self.logo_pixmap.isNull():
            print("Ошибка: не удалось загрузить файл assets/textures/logo2.png")
        else:
            self.logo_label.setPixmap(
                self.logo_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setGeometry(0, 0, self.width(), self.height())
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.show()
            self.fade(self.logo_label, duration=4500)

        # Добавляем задержку перед воспроизведением музыки интро
        QTimer.singleShot(10, lambda: self.parent.play_intro_music())

        QTimer.singleShot(4500, self.finish_intro)

    def finish_intro(self):
        """Завершение интро и показ меню."""
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
            self.leaderboard_button,
            self.settings_button,
            self.exit_button
        ]:
            widget.show()
            self.fade(widget, duration=600)

        # Останавливаем музыку интро
        if self.parent:
            self.parent.stop_intro_music()

        # Устанавливаем флаг завершения интро
        self.is_intro_finished = True

        # Запускаем музыку главного меню с задержкой
        QTimer.singleShot(500, lambda: self.parent.play_music(self.parent.menu_music_path))

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

    def load_username(self):
        """Загружает имя пользователя из leaderboard.json."""
        try:
            with open('config/leaderboard.json', 'r') as file:
                data = json.load(file)
                self.username = data.get("username", "ABC")  # По умолчанию "ABC"
        except FileNotFoundError:
            # Если файл не существует, создаем его с дефолтным именем
            self.username = "ABC"
            self.save_username_to_file()

    def save_username_to_file(self):
        """Сохраняет имя пользователя в leaderboard.json."""
        try:
            with open('config/leaderboard.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data["username"] = self.username

        with open('config/leaderboard.json', 'w') as file:
            json.dump(data, file, indent=4)

    def edit_username(self, event):
        """Переключение в режим редактирования имени."""
        if self.parent:
            self.parent.play_select_sound()  # Воспроизведение звука select_click
        self.username_label.hide()
        self.username_edit.setText(self.username_label.text())
        self.username_edit.move(self.width() - 200, self.height() - 50)
        self.username_edit.show()
        self.username_edit.setFocus()

    def validate_username(self):
        """
        Проверяет длину имени и меняет стиль QLineEdit.
        Если длина меньше 3, рамка становится красной.
        """
        text = self.username_edit.text()
        if len(text) < 3:
            self.username_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 0, 0, 0.8);  /* Красная рамка */
                    border-radius: 8px;
                    color: white;
                    font-size: 24px;
                    padding: 5px;
                }
                QLineEdit:focus {
                    border: 2px solid rgba(255, 0, 0, 0.8);  /* Красная рамка при фокусе */
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
        else:
            self.username_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 255, 255, 0.8);  /* Белая рамка */
                    border-radius: 8px;
                    color: white;
                    font-size: 24px;
                    padding: 5px;
                }
                QLineEdit:focus {
                    border: 2px solid rgba(0, 255, 255, 0.8);  /* Голубая рамка при фокусе */
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)

    def save_username(self):
        """
        Сохраняет новое имя пользователя.
        Если длина имени не равна 3, выводит сообщение об ошибке.
        """
        new_name = self.username_edit.text().upper()  # Преобразуем в верхний регистр
        if len(new_name) == 3:  # Проверяем длину имени (ровно 3 символа)
            self.username = new_name
            self.username_label.setText(new_name)
            self.username_edit.hide()
            self.username_label.show()
            self.save_username_to_file()  # Сохраняем имя в файл
        else:
            print("Ошибка: имя должно содержать ровно 3 символа.")
            self.validate_username()  # Подсвечиваем красную рамку
    def create_button(self, text, callback, x, y, w, h):
        button = QPushButton(text, self)
        button.setFont(QFont("Montserrat", 20))
        button.clicked.connect(lambda: self.play_button_sound_and_callback(callback))  # Обновленная строка
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

    def play_button_sound_and_callback(self, callback):
        """
        Воспроизведение звука кнопки и выполнение связанного действия.
        """
        if self.parent:
            # Определяем, какую кнопку нажали
            if callback.__name__ == "open_settings" or callback.__name__ == "open_leaderboard":
                self.parent.play_select_sound()  # Звук для обычных кнопок
            elif callback.__name__ == "exit_game":
                self.parent.play_cancel_sound()  # Звук для кнопки "Выход"
            else:
                self.parent.play_select_sound()  # Звук по умолчанию

        callback()  # Выполнение связанного действия

    def create_label(self, text, font_size=18, bold=False, x=0, y=0, w=200, h=50):
        label = QLabel(text, self)
        font = QFont("Consolas", font_size)
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
        self.current_mode = "single"  # Устанавливаем режим на одиночный

    def animate_left_panel_out(self):
        widgets_to_move = [
            self.gradient_label,
            self.title_label,
            self.start_button,
            self.start_duo_button,
            self.leaderboard_button,
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
        self.title_label.move(0, 220)
        b_x = 25
        b_y = 450
        self.start_button.move(b_x, b_y)
        self.start_duo_button.move(b_x, b_y + 80)
        self.leaderboard_button.move(b_x, b_y + 160)
        self.settings_button.move(b_x, b_y + 240)
        self.exit_button.move(b_x, b_y + 320)

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
        self.current_mode = "duo"  # Устанавливаем режим на дуо

    def open_leaderboard(self):
        """Открытие или закрытие таблицы рекордов."""
        print("Обработка таблицы рекордов...")
        if self.is_leaderboard_open:
            # Если таблица рекордов уже открыта, закрываем её
            if self.parent:
                self.parent.play_cancel_sound()  # Воспроизведение звука cancel_click
            self.close_leaderboard()
            return

        # Если таблица рекордов не открыта, открываем её
        if self.parent:
            self.parent.play_select_sound()  # Воспроизведение звука select_click

        # Закрываем другие модальные окна, если они открыты
        self.close_settings()

        # Создаем прозрачный слой, если его еще нет
        if not self.overlay:
            self.overlay = QWidget(self)
            self.overlay.setGeometry(800, 0, 1120, 1080)  # Правая часть экрана
            self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
            self.overlay.hide()

        # Создаем виджет таблицы рекордов
        if not self.leaderboard_widget:
            self.leaderboard_widget = LeaderboardScreen(parent=self.parent)
            self.leaderboard_widget.setParent(self.overlay)  # Размещаем настройки на overlay
            self.leaderboard_widget.move(50, 240)  # Центрируем по вертикали и горизонтали
            self.leaderboard_widget.setFixedSize(1020, 600)

        # Показываем overlay и виджет таблицы рекордов
        self.overlay.show()
        self.leaderboard_widget.show()
        self.is_leaderboard_open = True  # Устанавливаем флаг, что таблица рекордов открыта

    def open_settings(self):
        """Открытие или закрытие экрана настроек."""
        print("Обработка настроек...")
        if self.is_settings_open:
            # Если настройки уже открыты, закрываем их
            if self.parent:
                self.parent.play_cancel_sound()  # Воспроизведение звука cancel_click
            self.close_settings()
            return

        # Если настройки не открыты, открываем их
        if self.parent:
            self.parent.play_select_sound()  # Воспроизведение звука select_click

        # Закрываем другие модальные окна, если они открыты
        self.close_leaderboard()

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

    def close_leaderboard(self):
        """Закрытие таблицы рекордов."""
        if self.leaderboard_widget:
            self.leaderboard_widget.hide()
        if self.overlay:
            self.overlay.hide()
        self.is_leaderboard_open = False

    def close_settings(self):
        """Закрытие экрана настроек."""
        if self.settings_menu:
            self.settings_menu.hide()
        if self.overlay:
            self.overlay.hide()
        self.is_settings_open = False


    def exit_game(self):
        print("Выход из игры...")
        if self.parent:
            self.parent.exit_game()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.is_leaderboard_open:
                self.close_leaderboard()
                self.parent.play_cancel_sound()
            elif self.is_settings_open:
                self.close_settings()
                self.parent.play_cancel_sound()

    def disable_buttons(self):
        for btn in [self.start_button, self.start_duo_button, self.leaderboard_button, self.settings_button, self.exit_button]:
            btn.setDisabled(True)

    def enable_buttons(self):
        for btn in [self.start_button, self.start_duo_button, self.leaderboard_button,  self.settings_button, self.exit_button]:
            btn.setDisabled(False)
