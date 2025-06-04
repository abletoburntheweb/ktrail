from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush
from engine.player import Player
from engine.obstacle import Obstacle, PowerLine


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

        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)
        self.obstacle_spawn_timer.start(2000)

        self.power_line = PowerLine(
            line_width=10,  # Ширина линий
            color=QColor(0, 255, 255)  # Голубой цвет
        )

        # Таймер для анимации движения тайлов (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # Обновление каждые ~16 мс (≈60 FPS)

        self.is_game_over = False

        self.debug_counter = 0
        self.debug_interval = 60  # Вывод раз в ~1 секунду (60 кадров ≈ 1 секунда)

        self.total_removed_obstacles = 0

        # Трейл игрока
        self.trail = []
        self.max_trail_length = 50
        self.trail_alpha_step = 255 // self.max_trail_length

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
        """Перемещение тайлов вниз и добавление новых."""
        new_tile_positions = []
        for x, y, color_index in self.tile_positions:
            y += 2
            if y <= self.height():
                new_tile_positions.append((x, y, color_index))

        if len(new_tile_positions) < 2:
            blue_tile_x = (self.columns // 2 - 2) * self.tile_size
            green_tile_x = (self.columns // 2 + 2) * self.tile_size

            # Добавляем новый синий тайл
            new_tile_positions.append((blue_tile_x, -self.tile_size, 1))  # 1 = индекс синего цвета
            # Добавляем новый зеленый тайл
            new_tile_positions.append((green_tile_x, -self.tile_size, 2))  # 2 = индекс зеленого цвета

        self.tile_positions = new_tile_positions

    def paintEvent(self, event):
        """Отрисовка тайлов, игрока, препятствий, трейла и линий."""
        painter = QPainter(self)

        # Отрисовка тайлов
        for x, y, color_index in self.tile_positions:
            color = self.tile_colors[color_index]
            painter.fillRect(x, y, self.tile_size, self.tile_size, color)

        # Отрисовка трейла игрока
        for i, (x, y) in enumerate(self.trail):
            # Нелинейное затухание (квадратичное)
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            color = QColor(0, 0, 0, max(0, alpha))
            painter.fillRect(x, y, self.player.size, self.player.size, QBrush(color))

        # Отрисовка игрока
        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))

        # Отрисовка препятствий
        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

        # Отрисовка линий PowerLine
        self.power_line.draw(painter, self.height())

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

        self.trail.insert(0, (self.player.x, self.player.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop()

        self.trail = [(x, y + 2) for x, y in self.trail]

        for obstacle in self.obstacles:
            obstacle.move()

        delete_y = 540
        initial_count = len(self.obstacles)
        removed_count = 0
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(delete_y)]
        removed_count = initial_count - len(self.obstacles)

        self.total_removed_obstacles += removed_count

        self.debug_counter += 1
        if self.debug_counter >= self.debug_interval:
            self.debug_counter = 0
            print(f"Суммарно удалено препятствий: {self.total_removed_obstacles}, осталось: {len(self.obstacles)}")

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
        self.trail.clear()
        self.is_game_over = False
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        self.total_removed_obstacles = 0

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