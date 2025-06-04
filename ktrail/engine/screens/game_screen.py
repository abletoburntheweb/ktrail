# engine/screens/game_screen.py

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from engine.player import Player

class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

        # Параметры для тайлов
        self.tile_size = 192
        self.rows = 6
        self.columns = 10
        self.tile_colors = [
            QColor(255, 0, 0),
            QColor(0, 0, 255),
            QColor(0, 255, 0),
            QColor(255, 255, 0),
            QColor(255, 0, 255),
            QColor(0, 255, 255),
            QColor(128, 0, 0),
            QColor(0, 128, 0),
            QColor(0, 0, 128),
            QColor(128, 128, 0)
        ]
        self.current_color_index = 0
        self.tile_positions = []

        self.player = Player()

        self.key_states = {
            Qt.Key_W: False,
            Qt.Key_S: False,
            Qt.Key_A: False,
            Qt.Key_D: False
        }

        self.initialize_tiles()

        # Таймер для анимации движения тайлов (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # Обновление каждые ~16 мс (≈60 FPS)

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def initialize_tiles(self):
        """Инициализация начальных позиций тайлов."""
        blue_tile_x = (self.columns // 2 - 2) * self.tile_size
        green_tile_x = (self.columns // 2 + 2) * self.tile_size

        y = 0

        # Добавляем синий тайл
        self.tile_positions.append((blue_tile_x, y, 1))  # 1 = индекс синего цвета
        # Добавляем зеленый тайл
        self.tile_positions.append((green_tile_x, y, 2))  # 2 = индекс зеленого цвета

    def move_tiles_down(self):
        """Перемещение тайлов вниз."""
        new_tile_positions = []
        for x, y, color_index in self.tile_positions:
            y += 2
            if y > self.height():
                y = -self.tile_size
            new_tile_positions.append((x, y, color_index))
        self.tile_positions = new_tile_positions

    def paintEvent(self, event):
        """Отрисовка тайлов и игрока."""
        painter = QPainter(self)

        for x, y, color_index in self.tile_positions:
            color = self.tile_colors[color_index]
            painter.fillRect(x, y, self.tile_size, self.tile_size, color)

        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш."""
        if event.key() == Qt.Key_Escape:
            print("Пауза...")
            self.toggle_pause()
        elif event.key() in self.key_states:
            self.key_states[event.key()] = True

    def keyReleaseEvent(self, event):
        """Обработка отпускания клавиш."""
        if event.key() in self.key_states:
            self.key_states[event.key()] = False

    def update_game(self):
        """Обновление игрового процесса."""
        for key, pressed in self.key_states.items():
            if pressed:
                self.player.move(key)
        self.move_tiles_down()
        self.update()

    def toggle_pause(self):
        """Переключение состояния паузы."""
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True

        if self.is_paused:
            self.timer.stop()
            if self.parent:
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)