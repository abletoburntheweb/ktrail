# engine/screens/game_logic.py
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStackedWidget, QApplication
from PyQt5.QtCore import Qt
import json

class GameEngine(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "config/settings.json"
        self.settings = self.load_settings()
        self.init_screens()

    def init_screens(self):
        """Инициализация экранов."""
        from engine.screens.main_menu import MainMenu
        from engine.screens.game_screen import GameScreen
        from engine.screens.pause_menu import PauseMenu
        from engine.screens.settings_menu import SettingsMenu
        from engine.screens.debug_menu import DebugMenuScreen

        self.main_menu = MainMenu(self)
        self.addWidget(self.main_menu)

        self.game_screen = GameScreen(self)
        self.addWidget(self.game_screen)

        self.settings_menu = SettingsMenu(self)
        self.addWidget(self.settings_menu)

        self.pause_menu = PauseMenu(self)
        self.addWidget(self.pause_menu)

        self.debug_menu = DebugMenuScreen(self)
        self.debug_menu.hide()

        if self.settings.get("fullscreen", False):
            self.set_fullscreen(True)
        else:
            self.set_fullscreen(False)

        self.setCurrentWidget(self.main_menu)

    def load_settings(self):
        default_settings = {"fullscreen": False}
        try:
            with open(self.settings_file, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Ошибка загрузки настроек. Используются настройки по умолчанию.")
        return default_settings

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def toggle_fullscreen(self):
        """Переключение между полноэкранным и оконным режимом."""
        if self.isFullScreen():
            self.set_fullscreen(False)
        else:
            self.set_fullscreen(True)

    def set_fullscreen(self, fullscreen):
        """Установка полноэкранного режима."""
        if fullscreen:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.showFullScreen()
            self.settings["fullscreen"] = True
        else:
            self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
            self.showNormal()
            self.settings["fullscreen"] = False
        self.save_settings()


    def toggle_pause(self):
        """Пауза игры."""
        if self.currentWidget() == self.game_screen:
            self.game_screen.toggle_pause()

    def exit_game(self):
        self.close()


    def interpolate_color(self, color1, color2, factor):
        """
        Интерполяция между двумя цветами.
        :param color1: Начальный цвет (QColor).
        :param color2: Конечный цвет (QColor).
        :param factor: Коэффициент интерполяции (0.0 - color1, 1.0 - color2).
        :return: Новый QColor.
        """
        r = int(color1.red() + (color2.red() - color1.red()) * factor)
        g = int(color1.green() + (color2.green() - color1.green()) * factor)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * factor)
        return QColor(r, g, b)