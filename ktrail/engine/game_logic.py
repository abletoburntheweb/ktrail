# engine/game_logic.py

import json
from PyQt5.QtWidgets import QStackedWidget
from engine.screens.main_menu import MainMenu
from engine.screens.game_screen import GameScreen
from engine.screens.pause_menu import PauseMenu
from engine.screens.settings_menu import SettingsMenu

class GameEngine(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "config/settings.json"
        self.settings = self.load_settings()
        self.init_screens()

    def init_screens(self):
        """Инициализация экранов."""
        self.main_menu = MainMenu(self)
        self.addWidget(self.main_menu)

        self.game_screen = GameScreen(self)
        self.addWidget(self.game_screen)

        self.settings_menu = SettingsMenu(self)
        self.addWidget(self.settings_menu)

        self.pause_menu = PauseMenu(self)
        self.addWidget(self.pause_menu)

        if self.settings.get("fullscreen", False):
            self.showFullScreen()
        else:
            self.showNormal()

        self.setCurrentWidget(self.main_menu)

    def load_settings(self):
        """Загрузка настроек из JSON-файла."""
        default_settings = {"fullscreen": False}
        try:
            with open(self.settings_file, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Ошибка загрузки настроек. Используются настройки по умолчанию.")
        return default_settings

    def save_settings(self):
        """Сохранение настроек в JSON-файл."""
        try:
            with open(self.settings_file, "w") as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима."""
        if self.isFullScreen():
            self.showNormal()
            self.settings["fullscreen"] = False
        else:
            self.showFullScreen()
            self.settings["fullscreen"] = True
        self.save_settings()

    def exit_game(self):
        """Выход из игры."""
        self.close()