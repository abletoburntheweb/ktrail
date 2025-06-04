# engine/game_screen.py

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush
from engine.player import Player
from engine.obstacle import Obstacle  # Импортируем класс Obstacle

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

        # Препятствия
        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)
        self.obstacle_spawn_timer.start(2000)  # Генерация нового препятствия каждые 2 секунды

        # Таймер для анимации движения тайлов (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # Обновление каждые ~16 мс (≈60 FPS)

        self.is_game_over = False

        self.reset_game()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def initialize_tiles(self):
        """Инициализация начальных позиций тайлов."""
        blue_tile_x = (self.columns // 2 - 2) * self.tile_size
        green_tile_x = (self.columns // 2 + 2) * self.tile_size

        y = 0

        self.tile_positions.append((blue_tile_x, y, 1))  # 1 = индекс синего цвета

        self.tile_positions.append((green_tile_x, y, 2))  # 2 = индекс зеленого цвета

    def spawn_obstacle(self):
        """Генерация нового препятствия."""
        if not self.is_game_over:
            obstacle = Obstacle(self.width(), self.height())
            self.obstacles.append(obstacle)

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
        """Отрисовка тайлов, игрока и препятствий."""
        painter = QPainter(self)

        for x, y, color_index in self.tile_positions:
            color = self.tile_colors[color_index]
            painter.fillRect(x, y, self.tile_size, self.tile_size, color)

        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))

        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

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
        if self.is_game_over:
            return

        for key, pressed in self.key_states.items():
            if pressed:
                self.player.move(key)

        for obstacle in self.obstacles:
            obstacle.move()

        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(self.height())]

        self.check_collisions()

        self.move_tiles_down()
        self.update()

    def check_collisions(self):
        """Проверка столкновений игрока с препятствиями."""
        if self.is_game_over:
            return

        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            if player_rect.intersects(obstacle.get_rect()):
                self.show_game_over()
                return

    def show_game_over(self):
        """Показывает сообщение о проигрыше."""
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer.stop()

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Конец игры")
        msg_box.setText("Вы проиграли!")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec_()

        if self.parent:
            self.parent.setCurrentWidget(self.parent.main_menu)

    def reset_game(self):
        """Сброс состояния игры."""
        self.player = Player()
        self.obstacles.clear()
        self.is_game_over = False
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        self.timer.start(16)
        self.obstacle_spawn_timer.start(2000)

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