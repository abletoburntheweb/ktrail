# engine/game_logic.py

from PyQt5.QtWidgets import QStackedWidget
from engine.screens.main_menu import MainMenu
from engine.screens.game_screen import GameScreen
from engine.screens.pause_menu import PauseMenu
from engine.screens.settings_menu import SettingsMenu

class GameEngine(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.init_screens()

    def init_screens(self):
        self.main_menu = MainMenu(self)
        self.addWidget(self.main_menu)

        self.game_screen = GameScreen(self)
        self.addWidget(self.game_screen)

        self.settings_menu = SettingsMenu(self)
        self.addWidget(self.settings_menu)

        self.pause_menu = PauseMenu(self)
        self.addWidget(self.pause_menu)

        self.setCurrentWidget(self.main_menu)

    def exit_game(self):
        self.close()