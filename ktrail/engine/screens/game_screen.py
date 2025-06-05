from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QRadialGradient

# Импорты других классов
from engine.day_night import DayNightSystem
from engine.player import Player
from engine.obstacle import Obstacle, PowerLine
from engine.tile_manager import TileManager  # Новый менеджер тайлов


class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Инициализация системы дня и ночи
        self.day_night = DayNightSystem()

        self.speed = 10

        self.init_ui()

        # Параметры для тайлов
        self.tile_size = 192
        self.rows = 6
        self.columns = 10

        # Инициализация TileManager
        self.tile_manager = TileManager(
            tile_size=self.tile_size,
            rows=self.rows,
            cols=self.columns,
            screen_width=self.width(),
            screen_height=self.height()
        )

        # Добавляем типы тайлов
        self.tile_manager.add_tile_type(
            "asphalt",
            [
                "assets/textures/asf.png",
                "assets/textures/dev_w.png",
                "assets/textures/dev_g.png"
            ],
            weights=[5, 3, 2]  # Частота появления текстур
        )
        self.tile_manager.add_tile_type("grass", ["assets/textures/grass.png"])

        self.tile_manager.init_tiles()  # Создаём начальные тайлы

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
        self.max_trail_length = 25

        # Таймер игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.is_game_over = False
        self.total_removed_obstacles = 0

        # Таймер обновления времени
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)
        self.time_timer.start(self.day_night.tick_interval_ms)

    def init_ui(self):
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_obstacle(self):
        """Генерация нового препятствия."""
        if not self.is_game_over:
            obstacle = Obstacle(self.width(), self.height())
            self.obstacles.append(obstacle)

    def paintEvent(self, event):
        """Отрисовка всего игрового экрана"""
        painter = QPainter(self)

        # 1. Рисуем тайлы
        self.tile_manager.draw_tiles(painter)

        # 2. Накладываем градиент дня/ночи
        gradient = self.day_night.get_background_gradient(self.height())
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # 3. Отрисовка линий
        self.power_line.draw(painter, self.height())

        # 4. Отрисовка трейла
        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            color = QColor(0, 0, 0, max(0, alpha))
            painter.fillRect(x, y, self.player.size, self.player.size, QBrush(color))

        # 5. Отрисовка игрока
        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))

        # 6. Отрисовка препятствий
        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

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
        self.trail = [(x, y + self.speed) for x, y in self.trail]

        # Движение препятствий
        for obstacle in self.obstacles:
            obstacle.move()

        # Удаление ушедших за экран
        initial_count = len(self.obstacles)
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(540)]
        self.total_removed_obstacles += initial_count - len(self.obstacles)

        # Проверка коллизий
        self.check_collisions()

        # Обновление позиций тайлов
        self.tile_manager.update_tiles(self.speed)

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
        self.tile_manager.init_tiles()

        self.day_night.current_tick = 8200

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