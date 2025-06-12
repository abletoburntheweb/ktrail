# engine/screens/game_logic.py
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QStackedWidget, QApplication
from PyQt5.QtCore import Qt, QUrl
import json

from engine.screens.game_screen import GameScreen
from engine.screens.leaderboard_screen import LeaderboardScreen
from engine.screens.main_menu import MainMenu


class GameEngine(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "config/settings.json"
        self.settings = self.load_settings()
        self.init_screens()

        # Инициализация медиа-плеера
        self.media_player = QMediaPlayer()
        self.current_music = None

        # Загрузка путей к музыке
        self.menu_music_path = "assets/audio/menu_music.mp3"
        self.game_music_path = "assets/audio/game_music.mp3"
        self.intro_music_path = "assets/audio/intro_music.mp3"

        # Установка начальной громкости
        initial_volume = self.settings.get("music_volume", 50)
        self.media_player.setVolume(initial_volume)

        # Подключение сигналов
        self.currentChanged.connect(self.on_screen_changed)



    def init_screens(self):
        """Инициализация экранов."""
        from engine.screens.main_menu import MainMenu
        from engine.screens.distance_selection import DistanceSelection
        from engine.screens.game_screen import GameScreen
        from engine.screens.game_screen_duo import GameScreenDuo
        from engine.screens.pause_menu import PauseMenu
        from engine.screens.settings_menu import SettingsMenu
        from engine.screens.debug_menu import DebugMenuScreen
        from engine.screens.leaderboard_screen import LeaderboardScreen  # Новый импорт

        self.main_menu = MainMenu(self)
        self.addWidget(self.main_menu)

        self.distance_selection = DistanceSelection(self)
        self.addWidget(self.distance_selection)

        self.game_screen = GameScreen(self)
        self.addWidget(self.game_screen)

        self.game_screen_duo = GameScreenDuo(self)
        self.addWidget(self.game_screen_duo)

        self.settings_menu = SettingsMenu(self)
        self.addWidget(self.settings_menu)

        self.pause_menu = PauseMenu(self)
        self.addWidget(self.pause_menu)

        self.debug_menu = DebugMenuScreen(self)
        self.debug_menu.hide()

        # Инициализация экрана таблицы рекордов
        self.leaderboard_screen = LeaderboardScreen(self)
        self.addWidget(self.leaderboard_screen)

        if self.settings.get("fullscreen", False):
            self.set_fullscreen(True)
        else:
            self.set_fullscreen(False)

        self.setCurrentWidget(self.main_menu)

    def load_settings(self):
        default_settings = {"fullscreen": False, "music_volume": 50}
        try:
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                settings.setdefault("music_volume", 50)
                return settings
        except (json.JSONDecodeError, FileNotFoundError):
            print("Ошибка загрузки настроек. Используются настройки по умолчанию.")
        return default_settings

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def play_intro_music(self):
        """Воспроизведение музыки интро."""
        print("Воспроизведение музыки интро...")
        self.stop_music()  # Останавливаем любую текущую музыку
        self.play_music(self.intro_music_path, loop=False)  # Запускаем intro_music без цикла

    def stop_intro_music(self):
        """Остановка музыки интро."""
        print("Остановка музыки интро...")
        if self.current_music == self.intro_music_path:
            self.stop_music()

    def play_music(self, music_path, loop=True):
        try:
            print(f"Попытка воспроизвести музыку: {music_path}")
            if self.current_music == music_path and self.media_player.state() == QMediaPlayer.PlayingState:
                print("Музыка уже играет. Ничего не делаем.")
                return

            self.media_player.stop()

            try:
                print("Отключение предыдущих сигналов...")
                self.media_player.mediaStatusChanged.disconnect()
            except TypeError:
                print("Нет предыдущих сигналов для отключения.")
                pass

            self.current_music = music_path
            media_content = QMediaContent(QUrl.fromLocalFile(music_path))
            self.media_player.setMedia(media_content)

            if loop:
                print("Подключение сигнала циклического воспроизведения...")
                self.media_player.mediaStatusChanged.connect(self.loop_music)

            # Устанавливаем громкость из настроек
            self.media_player.setVolume(self.settings.get("music_volume", 50))

            # Всегда переходим в начало трека
            self.media_player.setPosition(0)
            print("Запуск воспроизведения...")
            self.media_player.play()

        except Exception as e:
            print(f"Ошибка воспроизведения музыки: {e}")

    def loop_music(self, status):
        # Когда трек заканчивается, начинаем его снова
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def stop_music(self):
        try:
            self.media_player.stop()
            try:
                self.media_player.mediaStatusChanged.disconnect()
            except TypeError:
                pass  # Нет существующих соединений
            self.current_music = None
        except Exception as e:
            print(f"Ошибка остановки музыки: {e}")

    def on_screen_changed(self, index):
        current_widget = self.widget(index)

        if isinstance(current_widget, MainMenu):
            # Проверяем, играет ли уже музыка главного меню
            if self.current_music != self.menu_music_path:
                print("Переключение на музыку главного меню...")
                self.stop_music()
                self.play_music(self.menu_music_path)
            else:
                print("Музыка главного меню уже играет.")

        elif isinstance(current_widget, GameScreen):
            # Проверяем, играет ли уже игровая музыка
            if self.current_music != self.game_music_path:
                print("Переключение на игровую музыку...")
                self.stop_music()
                self.play_music(self.game_music_path)
            else:
                print("Игровая музыка уже играет.")

        elif isinstance(current_widget, LeaderboardScreen):
            # При необходимости можно оставить текущую музыку или изменить её
            print("Переключение на экран таблицы рекордов...")
            # Если нужна своя музыка для таблицы рекордов, раскомментируйте следующие строки:
            # leaderboard_music_path = "assets/audio/leaderboard_music.mp3"
            # self.play_music(leaderboard_music_path)

        # Останавливаем музыку интро при любом переключении экрана
        if self.current_music == self.intro_music_path:
            self.stop_intro_music()

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
        self.media_player.stop()
        self.close()

    @staticmethod
    def interpolate_color(color1, color2, factor):
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
