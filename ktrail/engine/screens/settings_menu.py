from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QSlider
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SettingsMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.previous_screen = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Настройки")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Полноэкранный режим
        self.fullscreen_toggle = QCheckBox("Полноэкранный режим")
        self.fullscreen_toggle.setFont(QFont("Arial", 18))
        self.fullscreen_toggle.setChecked(self.parent.settings.get("fullscreen", False))
        self.fullscreen_toggle.stateChanged.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_toggle)

        # Регулировка громкости
        volume_label = QLabel("Громкость музыки")
        volume_label.setFont(QFont("Arial", 18))
        layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.parent.settings.get("music_volume", 50))  # Значение по умолчанию 50%
        self.volume_slider.valueChanged.connect(self.update_music_volume)
        layout.addWidget(self.volume_slider)

        # Регулировка громкости звуковых эффектов
        effects_label = QLabel("Громкость звуков")
        effects_label.setFont(QFont("Arial", 18))
        layout.addWidget(effects_label)

        self.effects_slider = QSlider(Qt.Horizontal)
        self.effects_slider.setMinimum(0)
        self.effects_slider.setMaximum(100)
        self.effects_slider.setValue(self.parent.settings.get("effects_volume", 80))  # Значение по умолчанию 80%
        self.effects_slider.valueChanged.connect(self.update_effects_volume)
        layout.addWidget(self.effects_slider)

        # Переключатель отображения FPS
        self.fps_toggle = QCheckBox("Отображать FPS")
        self.fps_toggle.setFont(QFont("Arial", 18))
        self.fps_toggle.setChecked(self.parent.settings.get("show_fps", True))  # Значение по умолчанию: True
        self.fps_toggle.stateChanged.connect(self.toggle_fps)
        layout.addWidget(self.fps_toggle)

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.return_to_previous_screen)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def toggle_fullscreen(self, state):
        """Переключение полноэкранного режима."""
        if self.parent:
            self.parent.toggle_fullscreen()

    def update_music_volume(self, value):
        """Обновление громкости музыки."""
        if self.parent:
            self.parent.media_player.setVolume(value)
            self.parent.settings["music_volume"] = value
            self.parent.save_settings()  # Сохраняем настройки
    def update_effects_volume(self, value):
        """Обновление громкости звуковых эффектов."""
        if self.parent:
            self.parent.sound_player.setVolume(value)  # Устанавливаем громкость для sound_player
            self.parent.settings["effects_volume"] = value
            self.parent.save_settings()  # Сохраняем настройки
    def toggle_fps(self, state):
        """Переключение отображения FPS."""
        if self.parent:
            self.parent.settings["show_fps"] = bool(state)  # Сохраняем состояние чекбокса
            self.parent.save_settings()  # Сохраняем настройки
            # Обновляем видимость FPS в обоих игровых экранах
            if hasattr(self.parent, "game_screen"):
                self.parent.game_screen.update_fps_visibility(bool(state))
            if hasattr(self.parent, "game_screen_duo"):
                self.parent.game_screen_duo.update_fps_visibility(bool(state))

    def set_previous_screen(self, screen_name):
        """Устанавливает предыдущий экран."""
        self.previous_screen = screen_name

    def return_to_previous_screen(self):
        """Возвращает пользователя на предыдущий экран."""
        if self.parent:
            self.parent.play_cancel_sound()  # Воспроизведение звука cancel_click
        if self.previous_screen == "pause_menu":
            print("Возвращение в меню паузы...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.pause_menu)
        elif self.previous_screen == "main_menu":
            print("Возвращение в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)
        else:
            print("Неизвестный предыдущий экран. Возвращаемся в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)