from engine.day_night import DayNightSystem
from engine.player import Player
from engine.obstacle import Obstacle, PowerLine

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QRadialGradient


class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Загрузка текстур
        self.asphalt_texture = QPixmap("assets/textures/asf.png")
        self.grass_texture = QPixmap("assets/textures/grass.png")

        # Инициализация системы дня и ночи
        self.day_night = DayNightSystem()

        self.init_ui()

        # Параметры для тайлов
        self.tile_size = 192
        self.rows = 6
        self.columns = 10

        self.initialize_tiles()

        # Игрок
        self.player = Player()

        # Клавиши
        self.key_states = {
            Qt.Key_W: False,
            Qt.Key_S: False,
            Qt.Key_A: False,
            Qt.Key_D: False
        }

        # Препятствия
        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)
        self.obstacle_spawn_timer.start(2000)

        # Линии
        self.power_line = PowerLine(line_width=10, color=QColor(0, 255, 255))

        # Трейл игрока
        self.trail = []
        self.max_trail_length = 50
        self.trail_alpha_step = 255 // self.max_trail_length

        # Таймер игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.is_game_over = False
        self.total_removed_obstacles = 0
        self.debug_counter = 0
        self.debug_interval = 60

        # Таймер обновления времени
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)
        self.time_timer.start(self.day_night.tick_interval_ms)

    def init_ui(self):
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def initialize_tiles(self):
        """Создаёт начальные тайлы по всей ширине"""
        self.tile_positions = []
        for row in range(self.rows):
            for col in range(self.columns):
                x = col * self.tile_size
                y = row * self.tile_size-1
                if col < 4:
                    tile_type = "asphalt"
                else:
                    tile_type = "grass"
                self.tile_positions.append((x, y, tile_type))

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def move_tiles_down(self):
        """Перемещение тайлов вниз и добавление новых сверху"""
        new_tile_positions = []
        for x, y, tile_type in self.tile_positions:
            y += 2
            if y <= self.height():
                new_tile_positions.append((x, y, tile_type))

        # Проверяем, нужно ли добавить новые тайлы сверху
        for col in range(self.columns):
            x = col * self.tile_size
            if col < 4:
                tile_type = "asphalt"
            else:
                tile_type = "grass"

            # Проверяем, есть ли уже тайл наверху
            top_y = -self.tile_size+1
            has_top_tile = any(x == tx and ty <= 0 and ty > -self.tile_size for tx, ty, _ in new_tile_positions)

            if not has_top_tile:
                new_tile_positions.append((x, top_y, tile_type))

        self.tile_positions = new_tile_positions

    def spawn_obstacle(self):
        """Генерация нового препятствия."""
        if not self.is_game_over:
            obstacle = Obstacle(self.width(), self.height())
            self.obstacles.append(obstacle)

    def paintEvent(self, event):
        """Отрисовка тайлов, игрока, препятствий, трейла и линий."""
        painter = QPainter(self)

        # 1. Рисуем тайлы с текстурами
        for x, y, tile_type in self.tile_positions:
            texture = self.asphalt_texture if tile_type == "asphalt" else self.grass_texture
            scaled = texture.scaled(self.tile_size, self.tile_size)
            painter.drawPixmap(x, y, scaled)

        # 2. Накладываем градиент дня/ночи
        gradient = self.day_night.get_background_gradient(self.height())
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # 3. Отрисовка трейла
        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            color = QColor(0, 0, 0, max(0, alpha))
            painter.fillRect(x, y, self.player.size, self.player.size, QBrush(color))

        # 4. Отрисовка игрока
        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))

        # 5. Отрисовка препятствий
        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

        # 6. Отрисовка линий
        self.power_line.draw(painter, self.height())

        # 7. Фонарь при переходе ночи
        if self.day_night.should_draw_light():
            light_pos = self.mapFromGlobal(self.cursor().pos())
            light_radius = 120
            light_gradient = QRadialGradient(light_pos, light_radius)
            light_gradient.setColorAt(0, QColor(255, 240, 200, 120))
            light_gradient.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(light_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos, light_radius, light_radius)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggle_pause()
        elif event.text() == '~':
            if self.parent:
                if self.parent.debug_menu.isVisible():
                    self.parent.debug_menu.hide()
                else:
                    self.parent.debug_menu.update_debug_info(self.day_night)
                    self.parent.debug_menu.show()
                    self.parent.debug_menu.raise_()
                    self.parent.debug_menu.setFocus()
        elif event.key() in self.key_states:
            self.key_states[event.key()] = True

    def keyReleaseEvent(self, event):
        if event.key() in self.key_states:
            self.key_states[event.key()] = False

    def update_game(self):
        if self.is_game_over:
            return

        # Движение игрока
        for key, pressed in self.key_states.items():
            if pressed:
                self.player.move(key)

        # Обновление трейла
        self.trail.insert(0, (self.player.x, self.player.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop()
        self.trail = [(x, y + 2) for x, y in self.trail]

        # Движение препятствий
        for obstacle in self.obstacles:
            obstacle.move()

        # Удаление ушедших за экран
        initial_count = len(self.obstacles)
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(540)]
        self.total_removed_obstacles += initial_count - len(self.obstacles)

        # Проверка коллизий
        self.check_collisions()

        # Перемещение тайлов
        self.move_tiles_down()
        self.update()

    def check_collisions(self):
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            if player_rect.intersects(obstacle.get_rect()):
                self.show_game_over()
                return

    def show_game_over(self):
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer.stop()

        msg = QMessageBox()
        msg.setWindowTitle("Конец игры")
        msg.setText("Вы проиграли!")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Critical)
        choice = msg.exec_()

        if choice == QMessageBox.Retry:
            self.reset_game()
            self.update()
        else:
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)

    def reset_game(self):
        """Сброс состояния игры и полный рестарт."""
        self.player = Player()
        self.obstacles.clear()
        self.trail.clear()
        self.is_game_over = False

        # Пересоздаём тайлы
        self.initialize_tiles()

        # Перезапускаем таймеры
        self.timer.start(16)
        self.obstacle_spawn_timer.start(2000)

        self.total_removed_obstacles = 0

    def toggle_pause(self):
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