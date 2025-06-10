# engine/screens/game_screen_duo.py
from random import choice
from time import perf_counter

from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtWidgets import QWidget,QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient

from engine.game_logic import GameEngine
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
        self.speed = 10  # Общая скорость для обоих игроков
        self.init_ui()

        # Добавляем переменные для расчета FPS
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update_time = perf_counter()

        # Тайлы
        self.tile_size = 192
        self.rows = 6
        self.columns = 10
        self.tile_manager = TileManager(
            tile_size=self.tile_size,
            rows=self.rows,
            cols=self.columns,
            screen_width=self.width(),
            screen_height=self.height()
        )
        self.tile_manager.add_tile_type(
            "asphalt",
            [
                "assets/textures/asf.png",
                "assets/textures/dev_w.png",
                "assets/textures/dev_g.png"
            ],
            weights=[5, 3, 2]
        )
        self.tile_manager.add_tile_type("grass", ["assets/textures/grass.png"])
        self.tile_manager.add_tile_type("grass_side", ["assets/textures/grass_side.png"])
        self.tile_manager.add_tile_type("decoration", ["assets/textures/dev_o.png"])

        # Игроки
        self.player1 = PlayerDuo(player_id=1, y=520)
        self.player2 = PlayerDuo(player_id=2, y=520)

        # Линии
        self.power_line_duo = PowerLineDuo(line_width=12, color="#89878c")

        # Трейлы для обоих игроков
        self.trail1 = []
        self.trail2 = []
        self.max_trail_length = 20
        self.trail_width = 10
        self.trail_color1 = QColor("#4aa0fc")  # голубой
        self.trail_color2 = QColor("#ff6b6b")  # красный
        self.trail_transition_speed = 5  # Скорость перехода трейла

        # Параметры трейла для player1
        self.current_trail_x1 = self.player1.x + 15
        self.target_trail_x1 = self.player1.x + 15

        # Параметры трейла для player2
        self.current_trail_x2 = self.player2.x + 15
        self.target_trail_x2 = self.player2.x + 15

        # Препятствия для каждого игрока
        self.obstacles1 = []  # Препятствия для player1
        self.obstacles2 = []  # Препятствия для player2

        # Таймеры
        self.timer = QTimer(self)  # Основной игровой таймер
        self.timer.timeout.connect(self.update_game)

        self.obstacle_spawn_timer1 = QTimer(self)  # Таймер спавна препятствий для player1
        self.obstacle_spawn_timer1.timeout.connect(self.spawn_obstacle1)

        self.obstacle_spawn_timer2 = QTimer(self)  # Таймер спавна препятствий для player2
        self.obstacle_spawn_timer2.timeout.connect(self.spawn_obstacle2)

        self.time_timer = QTimer(self)  # Таймер обновления времени (день/ночь)
        self.time_timer.timeout.connect(self.update_day_night)

        # Состояние игры
        self.is_game_over = False

        # ВАЖНО: Таймеры НЕ запускаются автоматически
        self.timer.stop()
        self.obstacle_spawn_timer1.stop()
        self.obstacle_spawn_timer2.stop()
        self.time_timer.stop()


        # Состояние игры
        self.is_game_over = False

    def init_ui(self):
        self.setWindowTitle("Дуо режим")
        self.setFixedSize(1920, 1080)

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_obstacle1(self):
        """Генерация нового препятствия для player1."""
        if not self.is_game_over:
            obstacle = ObstacleDuo()
            obstacle.x = choice([600, 700, 800])  # Только левая сторона
            self.obstacles1.append(obstacle)

    def spawn_obstacle2(self):
        """Генерация нового препятствия для player2."""
        if not self.is_game_over:
            obstacle = ObstacleDuo()
            obstacle.x = choice([1100, 1200, 1300])  # Только правая сторона
            self.obstacles2.append(obstacle)

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

        # Рисуем разделитель
        separator_width = 50  # Ширина разделителя
        separator_x = self.width() // 2 - separator_width // 2  # Центр экрана
        separator_rect = QRect(separator_x, 0, separator_width, self.height())
        painter.fillRect(separator_rect, QBrush(QColor(128, 128, 128)))  # Серый цвет

        # Рисуем игроков
        painter.fillRect(self.player1.get_rect(), QBrush(Qt.red))
        painter.fillRect(self.player2.get_rect(), QBrush(Qt.blue))

        # Рисуем препятствия для player1
        for obstacle in self.obstacles1:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

        # Рисуем препятствия для player2
        for obstacle in self.obstacles2:
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

        # Отображение FPS
        fps_text = f"FPS: {self.fps:.1f}"
        painter.drawText(10, 30, fps_text)

    def draw_trail(self, painter, trail, color):
        start_color = color
        end_color = QColor("#FFFFFF")
        for i, (x, y) in enumerate(trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length
            interpolated_color = GameEngine.interpolate_color(start_color, end_color, factor)
            interpolated_color.setAlpha(max(0, alpha))
            painter.fillRect(x, y, self.trail_width, self.trail_width, QBrush(interpolated_color))

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
        else:
            # Управление игроками
            self.player1.move(event.key())
            self.player2.move(event.key())

            # Обновление целевых координат X для трейлов
            self.target_trail_x1 = self.player1.x + 15
            self.target_trail_x2 = self.player2.x + 15

            # Изменение скорости
            if event.key() in [Qt.Key_W, Qt.Key_Up]:  # Увеличение скорости
                self.player1.change_speed(Qt.Key_W)
                self.player2.change_speed(Qt.Key_Up)
                self.speed = self.player1.get_current_speed()  # Синхронизация скорости
            elif event.key() in [Qt.Key_S, Qt.Key_Down]:  # Уменьшение скорости
                self.player1.change_speed(Qt.Key_S)
                self.player2.change_speed(Qt.Key_Down)
                self.speed = self.player1.get_current_speed()  # Синхронизация скорости

    def set_target_distance(self, distance):
        self.target_distance = distance
        self.distance_traveled = 0

        # Запуск таймеров игры
        self.timer.start(16)
        self.time_timer.start(self.day_night.tick_interval_ms)

        # Запуск таймеров спавна препятствий
        self.obstacle_spawn_timer1.start(2000)  # Спавн каждые 2 секунды для player1
        self.obstacle_spawn_timer2.start(2000)  # Спавн каждые 2 секунды для player2

    def update_game(self):
        if self.is_game_over:
            return

        # Обновление пройденного расстояния
        self.distance_traveled += self.meters_per_frame
        if self.distance_traveled >= self.target_distance:
            self.show_victory()
            return

        # Обновление трейлов для обоих игроков
        self.current_trail_x1 = self.update_trail(
            self.player1, self.trail1, self.current_trail_x1, self.target_trail_x1, self.trail_color1
        )
        self.current_trail_x2 = self.update_trail(
            self.player2, self.trail2, self.current_trail_x2, self.target_trail_x2, self.trail_color2
        )

        # Передвижение препятствий для player1
        for obstacle in self.obstacles1:
            obstacle.move()
        self.obstacles1 = [o for o in self.obstacles1 if not o.is_off_screen()]

        # Передвижение препятствий для player2
        for obstacle in self.obstacles2:
            obstacle.move()
        self.obstacles2 = [o for o in self.obstacles2 if not o.is_off_screen()]

        # Проверка столкновений
        self.check_collisions()

        # Обновление тайлов
        self.tile_manager.update_tiles(self.speed)

        # Подсчет FPS
        self.frame_count += 1
        current_time = perf_counter()
        elapsed_time = current_time - self.last_fps_update_time

        if elapsed_time >= 1.0:  # Обновляем FPS каждую секунду
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_fps_update_time = current_time

        self.update()

    def update_trail(self, player, trail, current_trail_x, target_trail_x, color):
        """
        Обновляет трейл для указанного игрока.
        :param player: Экземпляр PlayerDuo.
        :param trail: Список точек трейла.
        :param current_trail_x: Текущая координата X трейла.
        :param target_trail_x: Целевая координата X трейла.
        :param color: Цвет трейла.
        """
        current_speed = player.get_current_speed()

        # Плавное обновление координаты X трейла
        if current_trail_x != target_trail_x:
            delta = target_trail_x - current_trail_x
            step = delta / self.trail_transition_speed
            current_trail_x += step

        # Добавление нескольких точек в трейл
        num_points = max(1, int(current_speed / 5))  # Количество точек зависит от скорости
        for i in range(num_points):
            factor = i / num_points  # Коэффициент интерполяции
            interpolated_x = int(current_trail_x + (target_trail_x - current_trail_x) * factor)
            y_offset = i * (player.speed // num_points)  # Смещение по Y для каждой точки
            trail.insert(0, (interpolated_x, player.y - y_offset))

        # Ограничение длины трейла
        if len(trail) > self.max_trail_length:
            trail.pop()

        # Сдвигаем все точки трейла вниз
        trail[:] = [(x, y + self.speed) for x, y in trail]

        return current_trail_x

    def check_collisions(self):
        p1_rect = self.player1.get_rect()
        p2_rect = self.player2.get_rect()

        # Проверка столкновений для player1
        for obstacle in self.obstacles1:
            rect = obstacle.get_rect()
            if p1_rect.intersects(rect):
                self.show_game_over("Игрок 1 проиграл!")
                return

        # Проверка столкновений для player2
        for obstacle in self.obstacles2:
            rect = obstacle.get_rect()
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
        """Сброс состояния игры и полный рестарт."""
        self.player1 = PlayerDuo(player_id=1)
        self.player2 = PlayerDuo(player_id=2)
        self.trail1.clear()
        self.trail2.clear()
        self.obstacles1.clear()  # Очищаем препятствия для player1
        self.obstacles2.clear()  # Очищаем препятствия для player2
        self.is_game_over = False
        self.distance_traveled = 0
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200

        # Запуск таймеров
        self.timer.start(16)  # Основной игровой таймер
        self.obstacle_spawn_timer1.start(2000)  # Спавн каждые 2 секунды для player1
        self.obstacle_spawn_timer2.start(2000)  # Спавн каждые 2 секунды для player2
        self.time_timer.start(self.day_night.tick_interval_ms)  # Таймер дня/ночи

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
