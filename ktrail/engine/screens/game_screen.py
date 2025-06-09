# engine/screens/game_screen.py

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QRadialGradient

from engine.car import Car
# Импорты других классов
from engine.day_night import DayNightSystem
from engine.player import Player
from engine.obstacle import Obstacle, PowerLine, ExposedWire, TransmissionTower, StreetLamp
from engine.tile_manager import TileManager  # Новый менеджер тайлов


class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Инициализация системы дня и ночи
        self.day_night = DayNightSystem()

        self.target_distance = 0  # Целевая дистанция
        self.distance_traveled = 0  # Пройденная дистанция
        self.speed_to_meters_coefficient = 0.01

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
        self.tile_manager.add_tile_type("grass_side", ["assets/textures/grass_side.png"])  # Текстура границы
        self.tile_manager.add_tile_type("decoration", ["assets/textures/dev_o.png"])  # Спрайт декорации

        # Создаём начальные тайлы
        self.tile_manager.init_tiles()

        # Игрок
        self.player = Player()

        # Опоры ЛЭП
        self.transmission_towers = []

        # Таймер для спавна опор ЛЭП
        self.tower_spawn_timer = QTimer(self)
        self.tower_spawn_timer.timeout.connect(self.spawn_transmission_tower)
        self.tower_spawn_timer.start(8000)  # Спавн каждые 8 секунд

        # Фонари
        self.street_lamps = []

        # Таймер для спавна фонарей
        self.lamp_spawn_timer = QTimer(self)
        self.lamp_spawn_timer.timeout.connect(self.spawn_street_lamp)
        self.lamp_spawn_timer.start(6000)  # Спавн каждые 6 секунд

        # Препятствия
        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)

        self.cars = []
        self.car_spawn_timer = QTimer(self)
        self.car_spawn_timer.timeout.connect(self.spawn_car)
        self.car_spawn_timer.start(5000)

        self.exposed_wires = []

        # Таймер для спавна оголенных проводов
        self.exposed_wire_spawn_timer = QTimer(self)
        self.exposed_wire_spawn_timer.timeout.connect(self.spawn_exposed_wire)
        self.exposed_wire_spawn_timer.start(3000)  # Спавн каждые 3 секунды

        # Линии
        self.power_line = PowerLine(line_width=12, color="#89878c")


        # Трейл игрока
        self.trail = []  # Трейл игрока
        self.max_trail_length = 35
        self.trail_width = 10
        self.trail_color = QColor("#4aa0fc")  # Цвет трейла (HEX)
        self.target_trail_x = self.player.x + 15  # Целевая координата X для трейла
        self.current_trail_x = self.player.x + 15  # Текущая координата X для трейла
        self.trail_transition_speed = 5  # Скорость перехода трейла

        # Таймер игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)

        # Таймер обновления времени
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)

        # Состояние игры
        self.is_game_over = False
        self.total_removed_obstacles = 0

        # ВАЖНО: Таймеры НЕ запускаются автоматически
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        self.time_timer.stop()

    def init_ui(self):
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_transmission_tower(self):
        """Генерация новой опоры ЛЭП."""
        if not self.is_game_over:
            tower = TransmissionTower(screen_height=self.height())
            self.transmission_towers.append(tower)
    def spawn_obstacle(self):
        """Генерация нового препятствия."""
        if not self.is_game_over:
            obstacle = Obstacle(self.width(), self.height())
            self.obstacles.append(obstacle)

    def spawn_exposed_wire(self):
        """Генерация нового оголенного провода."""
        if not self.is_game_over:
            exposed_wire = ExposedWire(self.width(), self.height())
            self.exposed_wires.append(exposed_wire)

    def spawn_street_lamp(self):
        """Генерация нового фонаря."""
        if not self.is_game_over:
            lamp = StreetLamp(self.width(), self.height())
            self.street_lamps.append(lamp)
    def spawn_car(self):
        """Генерация новой машины (двигается снизу вверх по правому ряду)"""
        if not self.is_game_over:
            car = Car(self.width(), self.height())
            self.cars.append(car)


    def paintEvent(self, event):
        """Отрисовка всего игрового экрана"""
        painter = QPainter(self)

        # 1. Рисуем тайлы
        self.tile_manager.draw_tiles(painter)

        # 2. Отрисовка машин
        for car in self.cars:
            painter.drawPixmap(car.x, car.y, car.texture)

        # 3. Накладываем градиент дня/ночи
        gradient = self.day_night.get_background_gradient(self.height())
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # 4. Отрисовка линий
        self.power_line.draw(painter, self.height())

        # 5. Отрисовка трейла
        start_color = QColor("#4aa0fc")  # Голубой
        end_color = QColor("#FFFFFF")   # Белый

        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length  # Коэффициент интерполяции
            interpolated_color = self.parent.interpolate_color(start_color, end_color, factor)
            interpolated_color.setAlpha(max(0, alpha))  # Устанавливаем прозрачность

            painter.fillRect(x, y, self.trail_width, self.trail_width, QBrush(interpolated_color))

        # 6. Отрисовка игрока
        painter.fillRect(self.player.get_rect(), QBrush(Qt.red))


        # 7. Отрисовка препятствий
        for obstacle in self.obstacles:
            painter.fillRect(obstacle.get_rect(), QBrush(Qt.black))
        # 8. Отрисовка опор ЛЭП
        for tower in self.transmission_towers:
            tower.draw(painter)

        # 9. Отрисовка оголенного провода
        for exposed_wire in self.exposed_wires:
            painter.fillRect(exposed_wire.get_rect(), QBrush(exposed_wire.color))

        for lamp in self.street_lamps:
            # Отрисовка самого фонаря
            painter.fillRect(lamp.get_rect(), QBrush(Qt.darkGray))
            # Отрисовка света фонаря
            lamp.draw_light(painter, self.height())

        # 10. Фонарь при переходе ночи
        if self.day_night.should_draw_light():
            light_pos = self.mapFromGlobal(self.cursor().pos())
            light_radius = 120
            light_gradient = QRadialGradient(light_pos, light_radius)
            light_gradient.setColorAt(0, QColor(255, 240, 200, 120))
            light_gradient.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(light_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos, light_radius, light_radius)

        if self.target_distance > 0:
            painter.setPen(QColor(255, 255, 255))
            text = f"Пройдено: {int(self.distance_traveled)} м / {self.target_distance} м"
            painter.drawText(1700, 50, text)

        painter.setPen(QColor(255, 255, 255))
        speed_text = f"Скорость: {self.player.get_current_speed()} м/с"
        painter.drawText(10, 30, speed_text)

    def keyPressEvent(self, event):
        """Обработка нажатия клавиш."""
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
        elif event.key() in [Qt.Key_A, Qt.Key_D]:  # Разрешаем только A и D
            self.player.move(event.key())
            # Обновляем целевую координату X для трейла
            self.target_trail_x = self.player.x + 15
        elif event.key() in [Qt.Key_W, Qt.Key_S]:  # Изменение скорости
            self.player.change_speed(event.key())

    def set_target_distance(self, distance):
        self.target_distance = distance
        self.distance_traveled = 0
        # Перезапуск таймеров и т.д.
        self.timer.start(16)
        self.obstacle_spawn_timer.start(2000)
        self.time_timer.start(self.day_night.tick_interval_ms)

    def update_game(self):
        """Обновление игрового процесса."""
        if self.is_game_over:
            return

        # Динамический расчет пройденного расстояния
        current_speed = self.player.get_current_speed()  # Текущая скорость игрока
        meters_this_frame = current_speed * self.speed_to_meters_coefficient
        self.distance_traveled += meters_this_frame

        # Проверка достижения целевой дистанции
        if self.distance_traveled >= self.target_distance:
            self.show_victory()
            return

        # Плавное обновление координаты X трейла
        if self.current_trail_x != self.target_trail_x:
            delta = self.target_trail_x - self.current_trail_x
            step = delta / self.trail_transition_speed
            self.current_trail_x += step

        # Добавление нескольких точек в трейл в зависимости от скорости
        num_points = max(1, int(current_speed / 5))  # Количество точек зависит от скорости
        for i in range(num_points):
            # Интерполяция координаты X для каждой точки
            factor = i / num_points  # Коэффициент интерполяции
            interpolated_x = int(self.current_trail_x + (self.target_trail_x - self.current_trail_x) * factor)
            # Добавляем новую точку с учетом смещения по Y
            y_offset = i * (self.player.speed // num_points)  # Смещение по Y для каждой точки
            self.trail.insert(0, (interpolated_x, self.player.y - y_offset))

        # Ограничение длины трейла
        if len(self.trail) > self.max_trail_length:
            self.trail = self.trail[:self.max_trail_length]

        # Сдвигаем все точки трейла вниз
        self.trail = [(x, y + self.player.speed) for x, y in self.trail]

        # Движение препятствий
        for obstacle in self.obstacles:
            obstacle.move()

        # Движение опор ЛЭП
        for tower in self.transmission_towers:
            tower.move(self.player.speed)

        # Удаление ушедших за экран опор ЛЭП
        initial_count = len(self.transmission_towers)
        self.transmission_towers = [tower for tower in self.transmission_towers if not tower.is_off_screen()]
        self.total_removed_obstacles += initial_count - len(self.transmission_towers)

        # Движение фонарей
        for lamp in self.street_lamps:
            lamp.move()
            lamp.update_light_state(self.day_night)

        # Удаление ушедших за экран фонарей
        initial_count = len(self.street_lamps)
        self.street_lamps = [lamp for lamp in self.street_lamps if not lamp.is_off_screen(540)]
        self.total_removed_obstacles += initial_count - len(self.street_lamps)

        # Удаление ушедших за экран
        initial_count = len(self.obstacles)
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(540)]
        self.total_removed_obstacles += initial_count - len(self.obstacles)

        for exposed_wire in self.exposed_wires:
            exposed_wire.move()

            # Удаление ушедших за экран оголенных проводов
        initial_count = len(self.exposed_wires)
        self.exposed_wires = [wire for wire in self.exposed_wires if not wire.is_off_screen(540)]
        self.total_removed_obstacles += initial_count - len(self.exposed_wires)


        # Движение машин
        for car in self.cars:
            car.move()

        # Удаление ушедших за экран машин
        self.cars = [car for car in self.cars if not car.is_off_screen()]

        # Проверка коллизий
        self.check_collisions()

        # Обновление позиций тайлов
        self.tile_manager.update_tiles(self.player.speed)

        self.update()

    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Проверка коллизий с обычными препятствиями
        for obstacle in self.obstacles:
            if player_rect.intersects(obstacle.get_rect()):
                self.show_game_over()
                return

        # Проверка коллизий с оголенными проводами
        for exposed_wire in self.exposed_wires:
            if player_rect.intersects(exposed_wire.get_rect()):
                self.show_game_over()
                return

    def show_victory(self):
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        msg = QMessageBox()
        msg.setWindowTitle("Победа!")
        msg.setText(f"Вы проехали {int(self.target_distance)} метров!")
        msg.setStandardButtons(QMessageBox.Ok)
        choice = msg.exec_()
        if choice == QMessageBox.Ok:
            self.target_distance = 0
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)

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
        self.cars.clear()
        self.trail.clear()
        self.exposed_wires.clear()  # Очищаем список оголенных проводов
        self.transmission_towers.clear()  # Очищаем список опор ЛЭП
        self.is_game_over = False
        self.distance_traveled = 0

        # Пересоздаём тайлы
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200

        # Запускаем таймеры
        self.timer.start(16)
        self.obstacle_spawn_timer.start(2000)
        self.time_timer.start(self.day_night.tick_interval_ms)

        # Сбрасываем счетчик удаленных препятствий
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