from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QSlider, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SettingsMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # Основной макет
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)  # Отступы между элементами

        # Заголовок
        title_label = QLabel("Настройки")
        title_label.setFont(QFont("Montserrat", 36, QFont.Bold))
        title_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(title_label)

        # Полноэкранный режим
        self.fullscreen_toggle = QCheckBox("Полноэкранный режим")
        self.fullscreen_toggle.setFont(QFont("Montserrat", 18))
        self.fullscreen_toggle.setStyleSheet("""
            QCheckBox {
                color: white;
                background-color: transparent;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid white;
                border-radius: 4px; /* Квадратные углы */
                background-color: rgba(255, 255, 255, 20); /* Белый фон по умолчанию */
            }
            QCheckBox::indicator:checked {
                background-color: black; /* Черный цвет при активации */
                border: 2px solid white;
            }
            QCheckBox::indicator:!checked {
                background-color: white; /* Белый цвет при деактивации */
                border: 2px solid white;
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(255, 255, 255, 150);
            }
        """)
        self.fullscreen_toggle.setChecked(self.parent.settings.get("fullscreen", False))
        self.fullscreen_toggle.stateChanged.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_toggle)

        # Регулировка громкости музыки
        volume_label = QLabel("Громкость музыки")
        volume_label.setFont(QFont("Montserrat", 18))
        volume_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.parent.settings.get("music_volume", 50))
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background-color: rgba(255, 255, 255, 50);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                margin: -6px 0;
                background-color: white;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background-color: rgba(255, 255, 255, 150);
                border-radius: 4px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.update_music_volume)
        layout.addWidget(self.volume_slider)

        # Регулировка громкости звуковых эффектов
        effects_label = QLabel("Громкость звуков")
        effects_label.setFont(QFont("Montserrat", 18))
        effects_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(effects_label)

        self.effects_slider = QSlider(Qt.Horizontal)
        self.effects_slider.setMinimum(0)
        self.effects_slider.setMaximum(100)
        self.effects_slider.setValue(self.parent.settings.get("effects_volume", 80))
        self.effects_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background-color: rgba(255, 255, 255, 50);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                margin: -6px 0;
                background-color: white;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background-color: rgba(255, 255, 255, 150);
                border-radius: 4px;
            }
        """)
        self.effects_slider.valueChanged.connect(self.update_effects_volume)
        layout.addWidget(self.effects_slider)

        # Переключатель отображения FPS
        self.fps_toggle = QCheckBox("Отображать FPS")
        self.fps_toggle.setFont(QFont("Montserrat", 18))
        self.fps_toggle.setStyleSheet("""
            QCheckBox {
                color: white;
                background-color: transparent;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid white;
                border-radius: 4px; /* Квадратные углы */
                background-color: rgba(255, 255, 255, 20); /* Белый фон по умолчанию */
            }
            QCheckBox::indicator:checked {
                background-color: black; /* Черный цвет при активации */
                border: 2px solid white;
            }
            QCheckBox::indicator:!checked {
                background-color: white; /* Белый цвет при деактивации */
                border: 2px solid white;
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(255, 255, 255, 150);
            }
        """)
        self.fps_toggle.setChecked(self.parent.settings.get("show_fps", True))
        self.fps_toggle.stateChanged.connect(self.toggle_fps)
        layout.addWidget(self.fps_toggle)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: rgba(255, 255, 255, 50);")
        layout.addWidget(separator)

        # Кнопка "Закрыть"
        close_button = QPushButton("Закрыть")
        close_button.setFont(QFont("Montserrat", 18))
        close_button.setStyleSheet("""
            color: white;
            background-color: rgba(255, 255, 255, 20);
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px;
        """)
        close_button.enterEvent = lambda e: close_button.setStyleSheet("""
            color: white;
            background-color: rgba(255, 255, 255, 40);
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px;
        """)
        close_button.leaveEvent = lambda e: close_button.setStyleSheet("""
            color: white;
            background-color: rgba(255, 255, 255, 20);
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px;
        """)
        close_button.clicked.connect(self.close_settings)
        layout.addWidget(close_button)

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
            self.parent.save_settings()

    def update_effects_volume(self, value):
        """Обновление громкости звуковых эффектов."""
        if self.parent:
            self.parent.sound_player.setVolume(value)
            self.parent.settings["effects_volume"] = value
            self.parent.save_settings()

    def toggle_fps(self, state):
        """Переключение отображения FPS."""
        if self.parent:
            self.parent.settings["show_fps"] = bool(state)  # Обновляем настройку
            self.parent.save_settings()  # Сохраняем настройку

            # Уведомляем GameScreen о новом состоянии FPS
            if hasattr(self.parent.game_screen, "update_fps_visibility"):
                self.parent.game_screen.update_fps_visibility(bool(state))

    def close_settings(self):
        """Закрытие экрана настроек."""
        if self.parent:
            self.parent.main_menu.close_settings()
            self.parent.play_cancel_sound()