# engine/screens/game_screen_duo.py

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget,QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient

from engine.player_duo import PlayerDuo
from engine.obstacle_duo import ObstacleDuo, PowerLineDuo
from engine.day_night import DayNightSystem
from engine.tile_manager import TileManager


class GameScreenDuo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.day_night = DayNightSystem()
        self.target_distance = 1000
        self.distance_traveled = 0
        self.meters_per_frame = 0.1
        self.speed = 10

        self.init_ui()

        # Тайлы
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
        self.tile_manager.add_tile_type("grass_side", ["assets/textures/grass_side.png"])  # Текстура границы
        self.tile_manager.add_tile_type("decoration", ["assets/textures/dev_o.png"])  # Спрайт декорации

        # Игроки
        self.player1 = PlayerDuo(player_id=1, y=520)  # Справа, WASD
        self.player2 = PlayerDuo(player_id=2, y=520)  # Слева, Стрелки

        # Клавиши
        self.key_states = {
            Qt.Key_A: False,
            Qt.Key_D: False,
            Qt.Key_Left: False,
            Qt.Key_Right: False,
        }

        self.power_line_duo = PowerLineDuo(line_width=12, color="#89878c")

        # Трейлы
        self.trail1 = []
        self.trail2 = []
        self.max_trail_length = 25
        self.trail_width = 10
        self.trail_color1 = QColor("#4aa0fc")  # голубой
        self.trail_color2 = QColor("#ff6b6b")  # красный

        # Препятствия
        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)

        # Трейлы
        self.trail1 = []
        self.trail2 = []
        self.max_trail_length = 25
        self.trail_width = 10
        self.trail_color1 = QColor("#4aa0fc")  # голубой
        self.trail_color2 = QColor("#ff6b6b")  # красный

        # Таймеры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)


        # Таймер обновления времени
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)

        # Состояние игры
        self.is_game_over = False

    def init_ui(self):
        self.setWindowTitle("Дуо режим")
        self.setFixedSize(1920, 1080)

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_obstacle(self):
        if not self.is_game_over:
            obstacle = ObstacleDuo()
            self.obstacles.append(obstacle)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Рисуем дорогу
        self.tile_manager.draw_tiles(painter)

        # Накладываем градиент дня/ночи
        gradient = self.day_night.get_background_gradient(self.height())
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # Рисуем линии движения
        self.power_line_duo.draw(painter, self.height())

        # Рисуем трейлы
        self.draw_trail(painter, self.trail1, self.trail_color1)
        self.draw_trail(painter, self.trail2, self.trail_color2)

        # Рисуем игроков
        painter.fillRect(self.player1.get_rect(), QBrush(Qt.red))
        painter.fillRect(self.player2.get_rect(), QBrush(Qt.blue))

        # Рисуем препятствия
        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

        # Фонарь ночью
        if self.day_night.should_draw_light():
            light_pos = self.mapFromGlobal(self.cursor().pos())
            light_radius = 120
            lg = QRadialGradient(light_pos, light_radius)
            lg.setColorAt(0, QColor(255, 240, 200, 120))
            lg.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(lg)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos, light_radius, light_radius)

        # Статистика
        painter.setPen(QColor(255, 255, 255))
        text = f"Пройдено: {int(self.distance_traveled)} м / {self.target_distance} м"
        painter.drawText(1700, 50, text)

    def draw_trail(self, painter, trail, color):
        start_color = color
        end_color = QColor("#FFFFFF")
        for i, (x, y) in enumerate(trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length
            interpolated_color = self.interpolate_color(start_color, end_color, factor)
            interpolated_color.setAlpha(max(0, alpha))
            painter.fillRect(x, y, self.trail_width, self.trail_width, QBrush(interpolated_color))

    @staticmethod
    def interpolate_color(c1, c2, t):
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)

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

    def set_target_distance(self, distance):
        self.target_distance = distance
        self.distance_traveled = 0
        self.timer.start(16)
        self.time_timer.start(self.day_night.tick_interval_ms)

    def update_game(self):
        if self.is_game_over:
            return

        self.distance_traveled += self.meters_per_frame
        if self.distance_traveled >= self.target_distance:
            self.show_victory()
            return

        # Управление игроками
        for key, pressed in self.key_states.items():
            if pressed:
                self.player1.move(key)
                self.player2.move(key)

        # Обновляем трейлы
        self.trail1.insert(0, (self.player1.x + 15, self.player1.y))
        if len(self.trail1) > self.max_trail_length:
            self.trail1.pop()
        self.trail1 = [(x, y + self.speed) for x, y in self.trail1]

        self.trail2.insert(0, (self.player2.x + 15, self.player2.y))
        if len(self.trail2) > self.max_trail_length:
            self.trail2.pop()
        self.trail2 = [(x, y + self.speed) for x, y in self.trail2]

        # Передвигаем препятствия
        for obstacle in self.obstacles:
            obstacle.move()
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        # Проверяем столкновения
        self.check_collisions()

        # Обновляем тайлы
        self.tile_manager.update_tiles(self.speed)

        self.update()

    def check_collisions(self):
        p1_rect = self.player1.get_rect()
        p2_rect = self.player2.get_rect()

        for obstacle in self.obstacles:
            rect = obstacle.get_rect()
            if p1_rect.intersects(rect):
                self.show_game_over("Игрок 1 проиграл!")
                return
            if p2_rect.intersects(rect):
                self.show_game_over("Игрок 2 проиграл!")
                return

    def show_victory(self):
        self.is_game_over = True
        self.timer.stop()
        msg = QMessageBox()
        msg.setWindowTitle("Победа!")
        msg.setText(f"Вы оба проехали {int(self.target_distance)} метров!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        if self.parent:
            self.parent.setCurrentWidget(self.parent.main_menu)

    def show_game_over(self, message="Кто-то проиграл"):
        self.is_game_over = True
        self.timer.stop()
        msg = QMessageBox()
        msg.setWindowTitle("Конец игры")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        choice = msg.exec_()
        if choice == QMessageBox.Retry:
            self.reset_game()
        else:
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)

    def reset_game(self):
        self.player1 = PlayerDuo(player_id=1)
        self.player2 = PlayerDuo(player_id=2)
        self.trail1.clear()
        self.trail2.clear()
        self.obstacles.clear()
        self.is_game_over = False
        self.distance_traveled = 0
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200
        self.timer.start(16)
        self.obstacle_spawn_timer.start(2000)
        self.time_timer.start(self.day_night.tick_interval_ms)

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