# engine/screens/game_screen_duo.py
from random import choice
from time import perf_counter

from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtWidgets import QWidget, QMessageBox, QProgressBar
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient, QFont

from engine.game_logic import GameEngine
from engine.player_duo import PlayerDuo
from engine.obstacle_duo import ObstacleDuo, PowerLineDuo, TransmissionTowerDuo, StreetLampDuo, ExposedWireDuo
from engine.day_night import DayNightSystem
from engine.tile_manager_duo import TileManagerDuo


class GameScreenDuo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.day_night = DayNightSystem()
        self.target_distance = 1000
        self.distance_traveled_player1 = 0
        self.distance_traveled_player2 = 0
        self.meters_per_frame = 0.1
        self.speed_to_meters_coefficient = 0.01  # Добавьте эту строку
        self.speed = 10  # Общая скорость для обоих игроков
        self.init_ui()

        # Добавляем переменные для расчета FPS
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update_time = perf_counter()
        self.show_fps = True

        # Тайлы
        self.tile_size = 192
        self.rows = 6
        self.columns = 10
        self.tile_manager = TileManagerDuo(
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

        # Прогресс-бар для шкалы КЗ левого игрока (синий)
        self.short_circuit_bar_player1 = QProgressBar(self)
        self.short_circuit_bar_player1.setGeometry(10, 10, 300, 20)  # Размеры прогресс-бара
        self.short_circuit_bar_player1.setMaximum(100)  # Максимальное значение
        self.short_circuit_bar_player1.setTextVisible(False)  # Отключаем текст
        self.short_circuit_bar_player1.setStyleSheet("""
                   QProgressBar {
                       border: 1px solid white;
                       border-radius: 5px;
                       background-color: rgba(0, 0, 0, 100);
                   }
                   QProgressBar::chunk {
                       background-color: blue;  /* Синий цвет для player1 */
                       border-radius: 5px;
                   }
               """)
        self.short_circuit_bar_player1.show()

        # Прогресс-бар для шкалы КЗ правого игрока (красный)
        self.short_circuit_bar_player2 = QProgressBar(self)
        self.short_circuit_bar_player2.setGeometry(self.width() - 310, 10, 300, 20)  # Размеры прогресс-бара
        self.short_circuit_bar_player2.setMaximum(100)  # Максимальное значение
        self.short_circuit_bar_player2.setTextVisible(False)  # Отключаем текст
        self.short_circuit_bar_player2.setStyleSheet("""
                   QProgressBar {
                       border: 1px solid white;
                       border-radius: 5px;
                       background-color: rgba(0, 0, 0, 100);
                   }
                   QProgressBar::chunk {
                       background-color: red;  /* Красный цвет для player2 */
                       border-radius: 5px;
                   }
               """)
        self.short_circuit_bar_player2.show()
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

        self.transmission_towers1 = []  # Опоры ЛЭП для player1
        self.transmission_towers2 = []  # Опоры ЛЭП для player2

        self.exposed_wires1 = []  # Оголенные провода для player1
        self.exposed_wires2 = []  # Оголенные провода для player2

        self.street_lamps1 = []  # Фонари для player1
        self.street_lamps2 = []  # Фонари для player2

        # Таймеры
        self.timer = QTimer(self)  # Основной игровой таймер
        self.timer.timeout.connect(self.update_game)

        self.obstacle_spawn_timer1 = QTimer(self)  # Таймер спавна препятствий для player1
        self.obstacle_spawn_timer1.timeout.connect(self.spawn_obstacle1)

        self.obstacle_spawn_timer2 = QTimer(self)  # Таймер спавна препятствий для player2
        self.obstacle_spawn_timer2.timeout.connect(self.spawn_obstacle2)

        self.time_timer = QTimer(self)  # Таймер обновления времени (день/ночь)
        self.time_timer.timeout.connect(self.update_day_night)

        # Таймеры спавна опор ЛЭП
        self.tower_spawn_timer1 = QTimer(self)
        self.tower_spawn_timer1.timeout.connect(self.spawn_transmission_tower1)
        self.tower_spawn_timer1.start(3000)  # Спавн каждые 3 секунды для player1

        self.tower_spawn_timer2 = QTimer(self)
        self.tower_spawn_timer2.timeout.connect(self.spawn_transmission_tower2)
        self.tower_spawn_timer2.start(3000)  # Спавн каждые 3 секунды для player2

        # Таймеры спавна фонарей
        self.lamp_spawn_timer1 = QTimer(self)
        self.lamp_spawn_timer1.timeout.connect(self.spawn_street_lamp1)
        self.lamp_spawn_timer2 = QTimer(self)
        self.lamp_spawn_timer2.timeout.connect(self.spawn_street_lamp2)

        # Запуск таймеров при старте игры
        self.lamp_spawn_timer1.start(6000)  # Спавн каждые 6 секунд для player1
        self.lamp_spawn_timer2.start(6000)  # Спавн каждые 6 секунд для player2

        # Таймеры спавна оголенных проводов
        self.exposed_wire_spawn_timer1 = QTimer(self)
        self.exposed_wire_spawn_timer1.timeout.connect(self.spawn_exposed_wire1)
        self.exposed_wire_spawn_timer2 = QTimer(self)
        self.exposed_wire_spawn_timer2.timeout.connect(self.spawn_exposed_wire2)

        # Запуск таймеров при старте игры
        self.exposed_wire_spawn_timer1.start(3000)  # Спавн каждые 3 секунды для player1
        self.exposed_wire_spawn_timer2.start(3000)  # Спавн каждые 3 секунды для player2

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
            obstacle.x = choice([1100, 1200, 1300])  # Правая сторона для player1
            self.obstacles1.append(obstacle)

    def spawn_obstacle2(self):
        """Генерация нового препятствия для player2."""
        if not self.is_game_over:
            obstacle = ObstacleDuo()
            obstacle.x = choice([600, 700, 800])  # Левая сторона для player2
            self.obstacles2.append(obstacle)

    def spawn_exposed_wire1(self):
        """Генерация нового оголенного провода для player1."""
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([1100, 1200, 1300])  # Правая сторона для player1
            self.exposed_wires1.append(wire)

    def spawn_exposed_wire2(self):
        """Генерация нового оголенного провода для player2."""
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([600, 700, 800])  # Левая сторона для player2
            self.exposed_wires2.append(wire)

    def spawn_transmission_tower1(self):
        """Генерация новой опоры ЛЭП для player1."""
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = choice([1100, 1200, 1300])  # Правая сторона для player1
            self.transmission_towers1.append(tower)

    def spawn_transmission_tower2(self):
        """Генерация новой опоры ЛЭП для player2."""
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = choice([600, 700, 800])  # Левая сторона для player2
            self.transmission_towers2.append(tower)

    def spawn_street_lamp1(self):
        """Генерация нового фонаря для player1."""
        if not self.is_game_over:
            lamp = StreetLampDuo(self.width(), self.height())
            lamp.x = choice([1100, 1200, 1300])  # Левая сторона для player1
            self.street_lamps1.append(lamp)

    def spawn_street_lamp2(self):
        """Генерация нового фонаря для player2."""
        if not self.is_game_over:
            lamp = StreetLampDuo(self.width(), self.height())
            lamp.x = choice([600, 700, 800])  # Правая сторона для player2
            self.street_lamps2.append(lamp)


    def spawn_street_lamp1(self):
        """Генерация нового фонаря для player1."""
        if not self.is_game_over:
            lamp = StreetLampDuo(self.width(), self.height())
            lamp.x_positions = [600, 700, 800]  # Левая сторона
            lamp.x = choice(lamp.x_positions)
            self.street_lamps1.append(lamp)

    def spawn_street_lamp2(self):
        """Генерация нового фонаря для player2."""
        if not self.is_game_over:
            lamp = StreetLampDuo(self.width(), self.height())
            lamp.x_positions = [1100, 1200, 1300]  # Правая сторона
            lamp.x = choice(lamp.x_positions)
            self.street_lamps2.append(lamp)

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

        if self.player1.is_visible:
            painter.fillRect(self.player1.get_rect(), QBrush(Qt.red))
        if self.player2.is_visible:
            painter.fillRect(self.player2.get_rect(), QBrush(Qt.blue))

        # Отрисовка прямоугольников коллизий для игроков
        painter.setPen(Qt.red)
        painter.drawRect(self.player1.get_rect())
        painter.drawRect(self.player2.get_rect())

        # Отрисовка прямоугольников коллизий для препятствий УДАЛИТЬ ПОЗЖЕ
        painter.setPen(Qt.blue)
        for obstacle in self.obstacles1 + self.obstacles2:
            painter.drawRect(obstacle.get_rect())

        # Рисуем препятствия для player1 и player2
        for obstacle in self.obstacles1:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))
        for obstacle in self.obstacles2:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))

        # Рисуем опоры ЛЭП для player1 и player2
        for tower in self.transmission_towers1:
            tower.draw(painter)
        for tower in self.transmission_towers2:
            tower.draw(painter)

        # Рисуем фонари для player1 и player2
        for lamp in self.street_lamps1:
            painter.fillRect(lamp.get_rect(), QBrush(Qt.darkGray))  # Основа фонаря
            lamp.draw_light(painter, self.height())  # Свет фонаря
        for lamp in self.street_lamps2:
            painter.fillRect(lamp.get_rect(), QBrush(Qt.darkGray))  # Основа фонаря
            lamp.draw_light(painter, self.height())  # Свет фонаря

        # Рисуем оголенные провода для player1 и player2
        for wire in self.exposed_wires1:
            painter.fillRect(wire.get_rect(), QBrush(wire.color))
        for wire in self.exposed_wires2:
            painter.fillRect(wire.get_rect(), QBrush(wire.color))

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

        # Отображение FPS
        if self.show_fps:
            painter.setPen(QColor(255, 255, 255))
            fps_text = f"FPS: {self.fps:.1f}"
            painter.drawText(10, 30, fps_text)

        # Отображение пройденного пути для player1 (красный, верхний правый угол)
        painter.setFont(QFont("Arial", 20))  # Определяем размер шрифта
        painter.setPen(self.trail_color2)  # Красный цвет трейла

        # Пройденное расстояние для player1
        text_player1 = f"Пройдено: {int(self.distance_traveled_player1)} м / {self.target_distance} м"
        text_width_player1 = painter.fontMetrics().width(text_player1)
        painter.drawText(self.width() - text_width_player1 - 20, 50, text_player1)

        # Скорость для player1
        speed_player1 = self.player1.get_current_speed()
        speed_text_player1 = f"Скорость: {speed_player1} м/с"
        speed_text_width_player1 = painter.fontMetrics().width(speed_text_player1)
        painter.drawText(self.width() - speed_text_width_player1 - 20, 80, speed_text_player1)

        # Отображение пройденного пути для player2 (синий, верхний левый угол)
        painter.setPen(self.trail_color1)  # Синий цвет трейла

        # Пройденное расстояние для player2
        text_player2 = f"Пройдено: {int(self.distance_traveled_player2)} м / {self.target_distance} м"
        painter.drawText(10, 50, text_player2)

        # Скорость для player2
        speed_player2 = self.player2.get_current_speed()
        speed_text_player2 = f"Скорость: {speed_player2} м/с"
        painter.drawText(10, 80, speed_text_player2)

        # Обновление прогресс-баров
        self.short_circuit_bar_player1.setValue(int(self.player1.get_short_circuit_level()))
        self.short_circuit_bar_player2.setValue(int(self.player2.get_short_circuit_level()))

    def update_fps_visibility(self, visible):
        """Обновляет видимость FPS."""
        self.show_fps = visible
        self.update()  # Перерисовываем экран

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
        else:
            # Управление игроками
            self.player1.move(event.key())
            self.player2.move(event.key())

            # Обновление целевых координат X для трейлов
            self.target_trail_x1 = self.player1.x + 15
            self.target_trail_x2 = self.player2.x + 15

            # Изменение скорости для player1 (справа)
            if event.key() in [Qt.Key_Up, Qt.Key_Down]:  # Увеличение/уменьшение скорости для player1
                self.player1.change_speed(event.key())

            # Изменение скорости для player2 (слева)
            if event.key() in [Qt.Key_W, Qt.Key_S]:  # Увеличение/уменьшение скорости для player2
                self.player2.change_speed(event.key())

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
        """Обновление состояния игры."""
        if self.is_game_over:
            return

        # Получаем скорости игроков
        speed_player1 = self.player1.get_current_speed()
        speed_player2 = self.player2.get_current_speed()

        # Обновление пройденного расстояния для каждого игрока
        meters_this_frame_player1 = speed_player1 * self.speed_to_meters_coefficient
        meters_this_frame_player2 = speed_player2 * self.speed_to_meters_coefficient

        # Учитываем штраф за столкновение или переполнение КЗ
        self.distance_traveled_player1 = max(0,
                                             self.distance_traveled_player1 + meters_this_frame_player1 - self.player1.distance_penalty)
        self.distance_traveled_player2 = max(0,
                                             self.distance_traveled_player2 + meters_this_frame_player2 - self.player2.distance_penalty)

        # Сбрасываем штраф после применения
        self.player1.distance_penalty = 0
        self.player2.distance_penalty = 0

        # Проверка достижения целевой дистанции
        if self.distance_traveled_player1 >= self.target_distance:
            self.show_victory(winner="Игрок 1")
            return
        elif self.distance_traveled_player2 >= self.target_distance:
            self.show_victory(winner="Игрок 2")
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
            obstacle.speed = self.player1.get_current_speed()  # Устанавливаем скорость препятствия равной скорости игрока
            obstacle.move()

        # Удаление препятствий, которые вышли за пределы экрана
        self.obstacles1 = [o for o in self.obstacles1 if not o.is_off_screen()]

        # Передвижение препятствий для player2
        for obstacle in self.obstacles2:
            obstacle.speed = self.player2.get_current_speed()  # Устанавливаем скорость препятствия равной скорости игрока
            obstacle.move()

        # Удаление препятствий, которые вышли за пределы экрана
        self.obstacles2 = [o for o in self.obstacles2 if not o.is_off_screen()]

        # Передвижение опор ЛЭП для player1
        for tower in self.transmission_towers1:
            tower.move(self.player1.get_current_speed())

        # Передвижение опор ЛЭП для player2
        for tower in self.transmission_towers2:
            tower.move(self.player2.get_current_speed())

        # Удаление ушедших за экран опор ЛЭП
        self.transmission_towers1 = [tower for tower in self.transmission_towers1 if not tower.is_off_screen()]
        self.transmission_towers2 = [tower for tower in self.transmission_towers2 if not tower.is_off_screen()]

        for wire in self.exposed_wires1:
            wire.move()
        for wire in self.exposed_wires2:
            wire.move()

        # Удаление ушедших за экран оголенных проводов
        self.exposed_wires1 = [wire for wire in self.exposed_wires1 if not wire.is_off_screen(540)]
        self.exposed_wires2 = [wire for wire in self.exposed_wires2 if not wire.is_off_screen(540)]

        for lamp in self.street_lamps1:
            lamp.move()
            lamp.update_light_state(self.day_night)
        for lamp in self.street_lamps2:
            lamp.move()
            lamp.update_light_state(self.day_night)

        # Удаление ушедших за экран фонарей
        self.street_lamps1 = [lamp for lamp in self.street_lamps1 if not lamp.is_off_screen(540)]
        self.street_lamps2 = [lamp for lamp in self.street_lamps2 if not lamp.is_off_screen(540)]

        # Проверка столкновений
        self.check_collisions()

        # Обновление тайлов
        self.tile_manager.update_tiles(speed_player1, speed_player2)

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
        current_speed = player.get_current_speed()  # Получаем текущую скорость игрока

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
            y_offset = i * (current_speed // num_points)  # Смещение по Y для каждой точки
            trail.insert(0, (interpolated_x, player.y - y_offset))

        # Ограничение длины трейла
        if len(trail) > self.max_trail_length:
            trail.pop()

        # Сдвигаем все точки трейла вниз
        trail[:] = [(x, y + current_speed) for x, y in trail]

        return current_trail_x

    def check_collisions(self):
        """Проверка коллизий."""
        p1_rect = self.player1.get_rect()
        p2_rect = self.player2.get_rect()

        # Проверка переполнения шкалы КЗ для player1
        if self.player1.get_short_circuit_level() >= self.player1.short_circuit_max:
            self.handle_collision(self.player1, self.distance_traveled_player1, 20)
            return

        # Проверка переполнения шкалы КЗ для player2
        if self.player2.get_short_circuit_level() >= self.player2.short_circuit_max:
            self.handle_collision(self.player2, self.distance_traveled_player2, 20)
            return

        # Проверка столкновений для player1
        for obstacle in self.obstacles1[:]:  # Используем копию списка для безопасного удаления
            rect = obstacle.get_rect()
            if p1_rect.intersects(rect) and not self.player1.is_invincible:
                self.handle_collision(self.player1, self.distance_traveled_player1, 20)
                self.obstacles1.remove(obstacle)  # Удаляем препятствие
                break

        for wire in self.exposed_wires1[:]:  # Используем копию списка для безопасного удаления
            rect = wire.get_rect()
            if p1_rect.intersects(rect) and not self.player1.is_invincible:
                self.handle_collision(self.player1, self.distance_traveled_player1, 20)
                self.exposed_wires1.remove(wire)  # Удаляем оголенный провод
                break

        # Проверка столкновений для player2
        for obstacle in self.obstacles2[:]:  # Используем копию списка для безопасного удаления
            rect = obstacle.get_rect()
            if p2_rect.intersects(rect) and not self.player2.is_invincible:
                self.handle_collision(self.player2, self.distance_traveled_player2, 20)
                self.obstacles2.remove(obstacle)  # Удаляем препятствие
                break

        for wire in self.exposed_wires2[:]:  # Используем копию списка для безопасного удаления
            rect = wire.get_rect()
            if p2_rect.intersects(rect) and not self.player2.is_invincible:
                self.handle_collision(self.player2, self.distance_traveled_player2, 20)
                self.exposed_wires2.remove(wire)  # Удаляем оголенный провод
                break

    def handle_collision(self, player, distance_traveled, penalty):
        """Обработка столкновения для указанного игрока."""
        player.apply_collision_penalty(penalty)  # Применяем штраф
        distance_traveled -= penalty  # Отбрасываем игрока назад
        player.enable_invincibility(5000)  # Включаем неуязвимость на 5 секунд

    def show_victory(self, winner=""):
        """Показ экрана победы."""
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer1.stop()
        self.obstacle_spawn_timer2.stop()
        self.time_timer.stop()

        msg = QMessageBox()
        msg.setWindowTitle("Победа!")
        msg.setText(f"{winner} первым достиг цели!")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Information)
        choice = msg.exec_()

        if choice == QMessageBox.Retry:
            self.reset_game()
            self.update()
        else:
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)

    def show_game_over(self, message="Кто-то проиграл"):
        """Показ экрана 'Конец игры'."""
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer1.stop()
        self.obstacle_spawn_timer2.stop()
        self.time_timer.stop()

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

        # Очистка списков объектов
        self.trail1.clear()
        self.trail2.clear()
        self.obstacles1.clear()  # Препятствия для player1
        self.obstacles2.clear()  # Препятствия для player2

        # Сброс параметров игры
        self.is_game_over = False
        self.distance_traveled_player1 = 0
        self.distance_traveled_player2 = 0
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200

        # Запуск таймеров
        self.timer.start(16)  # Основной игровой таймер
        self.obstacle_spawn_timer1.start(2000)  # Спавн каждые 2 секунды для player1
        self.obstacle_spawn_timer2.start(2000)  # Спавн каждые 2 секунды для player2
        self.time_timer.start(self.day_night.tick_interval_ms)  # Таймер дня/ночи

        # Сброс шкалы КЗ
        self.short_circuit_bar_player1.setValue(0)
        self.short_circuit_bar_player2.setValue(0)

    def toggle_pause(self):
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True

        if self.is_paused:
            self.timer.stop()
            if self.parent:
                self.parent.main_menu.current_mode = "duo"
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)
