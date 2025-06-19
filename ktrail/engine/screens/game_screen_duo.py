# engine/screens/game_screen_duo.py
from random import choice
from time import perf_counter
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtWidgets import QWidget, QMessageBox, QProgressBar, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient, QFont, QPixmap

from engine.player_duo import PlayerDuo
from engine.obstacle_duo import ObstacleDuo, PowerLineDuo, TransmissionTowerDuo, ExposedWireDuo, Seporator
from engine.day_night import DayNightSystem
from engine.tile_manager_duo import TileManagerDuo
from collections import deque

class GameScreenDuo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.day_night = DayNightSystem()
        self.target_distance = 1000
        self.distance_traveled_player1 = 0
        self.distance_traveled_player2 = 0
        self.meters_per_frame = 0.1
        self.speed_to_meters_coefficient = 0.3
        self.speed = 10
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
        # Инициализация TileManager
        self.tile_manager = TileManagerDuo(
            tile_size=self.tile_size,
            rows=self.rows,
            cols=self.columns,
            screen_width=self.width(),
            screen_height=self.height()
        )

        self.tile_manager.load_default_tile_types()
        # Создаём начальные тайлы
        self.tile_manager.init_tiles()
        # Игроки
        self.player1 = PlayerDuo(player_id=1)
        self.player2 = PlayerDuo(player_id=2)
        # Прогресс-бар для шкалы КЗ левого игрока (синий)
        self.short_circuit_bar_player1 = QProgressBar(self)
        self.short_circuit_bar_player1.setGeometry(10, 10, 300, 20)  # Размеры прогресс-бара
        self.short_circuit_bar_player1.setMaximum(100)  # Максимальное значение
        self.short_circuit_bar_player1.setValue(0)  # Начальное значение
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
        self.short_circuit_bar_player2.setValue(0)  # Начальное значение
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
        self.power_line_duo = PowerLineDuo()


        #Сепо
        self.sepo = Seporator()

        self.init_side_panels()

        # Трейлы для обоих игроков
        self.max_trail_length = 20  # Максимальная длина трейла
        self.trail1 = []  # Используем list вместо deque
        self.trail2 = []  # Используем list вместо deque
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

        self.tower_spawn_timer2 = QTimer(self)
        self.tower_spawn_timer2.timeout.connect(self.spawn_transmission_tower2)
        # Таймеры спавна оголенных проводов
        self.exposed_wire_spawn_timer1 = QTimer(self)
        self.exposed_wire_spawn_timer1.timeout.connect(self.spawn_exposed_wire1)
        self.exposed_wire_spawn_timer2 = QTimer(self)
        self.exposed_wire_spawn_timer2.timeout.connect(self.spawn_exposed_wire2)
        # Состояние игры
        self.is_game_over = False
        # Создание объектов QPainter и QBrush один раз
        self.painter = QPainter()
        self.player1_brush = QBrush(Qt.red)
        self.player2_brush = QBrush(Qt.blue)
        self.obstacle_brush = QBrush(Qt.black)
        self.street_lamp_brush = QBrush(Qt.darkGray)
        self.separator_brush = QBrush(QColor(128, 128, 128))  # Серый цвет разделителя
        self.trail_start_color1 = QColor("#4aa0fc")  # Голубой
        self.trail_end_color1 = QColor("#FFFFFF")  # Белый
        self.trail_start_color2 = QColor("#ff6b6b")  # Красный
        self.trail_end_color2 = QColor("#FFFFFF")  # Белый
        self.font = QFont("Arial", 20)  # Определяем размер шрифта
        self.light_gradient = QRadialGradient()  # Создаем градиент один раз

    def init_ui(self):
        self.setWindowTitle("Дуо режим")
        self.setFixedSize(1920, 1080)

    def init_side_panels(self):
        """Инициализация боковых панелей."""
        self.setFixedSize(1920, 1080)
        # Правая панель
        self.right_panel = QLabel(self)
        right_panel_pixmap = QPixmap("assets/textures/side_panel_duo.png")
        if not right_panel_pixmap.isNull():
            self.right_panel.setPixmap(right_panel_pixmap)
            self.right_panel.setScaledContents(True)
            self.right_panel.setGeometry(
                self.width() - right_panel_pixmap.width(),
                0,
                right_panel_pixmap.width(),
                right_panel_pixmap.height()
            )
        else:
            print("Ошибка: Изображение правой панели не загружено!")

        # Левая панель
        self.left_panel = QLabel(self)
        left_panel_pixmap = QPixmap("assets/textures/side_panel_left_duo.png")
        if not left_panel_pixmap.isNull():
            self.left_panel.setPixmap(left_panel_pixmap)
            self.left_panel.setScaledContents(True)
            self.left_panel.setGeometry(
                0,
                0,
                left_panel_pixmap.width(),
                left_panel_pixmap.height()
            )
        else:
            print("Ошибка: Изображение левой панели не загружено!")

        # Создаем контейнеры для виджетов на боковых панелях
        # Правая панель
        self.side_panel_container = QWidget(self)
        self.side_panel_container.setGeometry(
            self.width() - right_panel_pixmap.width(),
            0,
            right_panel_pixmap.width(),
            right_panel_pixmap.height()
        )
        self.side_panel_container.setStyleSheet("background-color: transparent;")
        self.side_panel_container.raise_()

        # Левая панель
        self.side_panel_left_container = QWidget(self)
        self.side_panel_left_container.setGeometry(
            0,
            0,
            left_panel_pixmap.width(),
            left_panel_pixmap.height()
        )
        self.side_panel_left_container.setStyleSheet("background-color: transparent;")
        self.side_panel_left_container.raise_()

        # Списки для хранения изображений speed и short circuit
        self.speed_images_player1 = []
        self.short_circuit_images_player1 = []
        self.speed_images_player2 = []
        self.short_circuit_images_player2 = []

        # Координаты для правого игрока
        self.short_circuit_rect_right = {
            'x': 95,
            'y': 60,
            'width': 60,
            'height': 70
        }
        self.speed_rect_right = {
            'x': 195,
            'y': 80,
            'width': 30,
            'height': 30
        }

        # Координаты для левого игрока
        self.short_circuit_rect_left = {
            'x': 480,
            'y': 60,
            'width': 60,
            'height': 70
        }
        self.speed_rect_left = {
            'x': 380,
            'y': 80,
            'width': 30,
            'height': 30
        }

        # Создание виджетов для правого игрока
        self.create_speed_labels(self.speed_rect_right, self.short_circuit_rect_right, is_right=True)

        # Создание виджетов для левого игрока
        self.create_speed_labels(self.speed_rect_left, self.short_circuit_rect_left, is_right=False)

    def create_speed_labels(self, speed_rect, short_circuit_rect, is_right):
        """Создание виджетов для отображения скорости и КЗ."""
        container = self.side_panel_container if is_right else self.side_panel_left_container

        # Виджеты для скорости (максимум 4 изображения)
        for _ in range(4):  # Максимум 4 изображения скорости
            image_path = "assets/textures/speed.png" if is_right else "assets/textures/speed2.png"
            labels = self.speed_images_player1 if is_right else self.speed_images_player2
            self.add_speed_image(labels, container, speed_rect)

        # Виджеты для КЗ (максимум 3 стадии)
        for i in range(3):  # Максимум 3 стадии КЗ
            image_path = f"assets/textures/{['f', 's', 't'][i]}_stage.png" if is_right else f"assets/textures/{['f', 's', 't'][i]}_stage2.png"
            labels = self.short_circuit_images_player1 if is_right else self.short_circuit_images_player2
            self.add_short_circuit_image(image_path, labels, container, short_circuit_rect)

    def add_speed_image(self, labels, container, rect):
        """Добавляет изображение скорости."""
        if len(labels) >= 4:  # Ограничение: максимум 4 изображения
            return

        image_path = "assets/textures/speed.png" if "speed2" not in str(labels) else "assets/textures/speed2.png"
        speed_image_label = QLabel(container)
        speed_image_pixmap = QPixmap(image_path)
        if speed_image_pixmap.isNull():
            print(f"Ошибка: Изображение {image_path} не загружено!")
            return

        speed_image_label.setPixmap(speed_image_pixmap)
        speed_image_label.setScaledContents(False)
        image_width = speed_image_pixmap.width()
        image_height = speed_image_pixmap.height()

        base_x = rect['x']
        base_y = rect['y']
        y_position = base_y if len(labels) == 0 else labels[-1].y() - image_height

        speed_image_label.setGeometry(base_x, y_position, image_width, image_height)
        speed_image_label.hide()  # Скрыть по умолчанию
        labels.append(speed_image_label)

    def add_short_circuit_image(self, image_path, labels, container, rect):
        """Добавляет изображение стадии КЗ."""
        short_circuit_image_label = QLabel(container)
        short_circuit_image_pixmap = QPixmap(image_path)
        if short_circuit_image_pixmap.isNull():
            print(f"Ошибка: Изображение {image_path} не загружено!")
            return

        short_circuit_image_label.setPixmap(short_circuit_image_pixmap)
        short_circuit_image_label.setScaledContents(False)
        image_width = short_circuit_image_pixmap.width()
        image_height = short_circuit_image_pixmap.height()

        base_x = rect['x']
        base_y = rect['y']
        y_position = base_y if len(labels) == 0 else labels[-1].y() - image_height

        short_circuit_image_label.setGeometry(base_x, y_position, image_width, image_height)
        short_circuit_image_label.hide()  # Скрыть по умолчанию
        labels.append(short_circuit_image_label)

    def remove_speed_image(self, labels):
        """Удаляет последнее изображение скорости."""
        if not labels:
            return
        last_label = labels.pop()
        last_label.deleteLater()

    def remove_short_circuit_image(self, labels):
        """Удаляет последнее изображение КЗ."""
        if not labels:
            return
        last_label = labels.pop()
        last_label.deleteLater()

    def update_speed_images(self, player, speed_images):
        """Обновление изображений скорости"""
        current_speed_level = player.get_current_speed_level()
        for i, image in enumerate(speed_images):
            if i < current_speed_level:
                image.show()
            else:
                image.hide()

    def update_short_circuit_images(self, player, short_circuit_images):
        """Обновление изображений КЗ"""
        short_circuit_level = player.get_short_circuit_level()
        if short_circuit_level >= 40 and short_circuit_level < 60:
            short_circuit_images[0].show()  # f_stage
            short_circuit_images[1].hide()  # s_stage
            short_circuit_images[2].hide()  # t_stage
        elif short_circuit_level >= 60 and short_circuit_level < 80:
            short_circuit_images[0].show()  # f_stage
            short_circuit_images[1].show()  # s_stage
            short_circuit_images[2].hide()  # t_stage
        elif short_circuit_level >= 80:
            short_circuit_images[0].show()  # f_stage
            short_circuit_images[1].show()  # s_stage
            short_circuit_images[2].show()  # t_stage
        else:
            for image in short_circuit_images:
                image.hide()
    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_obstacle1(self):
        """Генерация нового препятствия для player1."""
        MAX_OBSTACLES_PER_PLAYER = 20
        if not self.is_game_over and len(self.obstacles1) < MAX_OBSTACLES_PER_PLAYER:
            obstacle = ObstacleDuo()
            obstacle.x = choice([1313, 1567, 1807])  # Правая сторона для player1
            self.obstacles1.append(obstacle)

    def spawn_obstacle2(self):
        """Генерация нового препятствия для player2."""
        MAX_OBSTACLES_PER_PLAYER = 20
        if not self.is_game_over and len(self.obstacles2) < MAX_OBSTACLES_PER_PLAYER:
            obstacle = ObstacleDuo()
            obstacle.x = choice([73, 327, 567])  # Левая сторона для player2
            self.obstacles2.append(obstacle)

    def spawn_exposed_wire1(self):
        """Генерация нового оголенного провода для player1."""
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([1313, 1567, 1807])
              # Правая сторона для player1
            self.exposed_wires1.append(wire)

    def spawn_exposed_wire2(self):
        """Генерация нового оголенного провода для player2."""
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([73, 327, 567])  # Левая сторона для player2
            self.exposed_wires2.append(wire)

    def spawn_transmission_tower1(self):
        """Генерация дополнительной опоры ЛЭП для player1."""
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = 40
            self.transmission_towers1.append(tower)

    def spawn_transmission_tower2(self):
        """Генерация дополнительной опоры ЛЭП для player2."""
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = 1280
            self.transmission_towers2.append(tower)

    def paintEvent(self, event):
        try:
            self.painter.begin(self)
            # Рисуем дорогу
            self.tile_manager.draw_tiles(self.painter)

            # Рисуем опоры ЛЭП для player1 и player2
            for tower in self.transmission_towers1:
                if tower:
                    tower.draw(self.painter)

            for tower in self.transmission_towers2:
                if tower:
                    tower.draw(self.painter)

            # Рисуем линии движения
            self.power_line_duo.draw(self.painter, self.height())

            # Рисуем оголенные провода для player1 и player2
            for wire in self.exposed_wires1:
                if wire:
                    wire.draw(self.painter)
            for wire in self.exposed_wires2:
                if wire:
                    wire.draw(self.painter)

            # Накладываем градиент дня/ночи
            gradient = self.day_night.get_background_gradient(self.height())
            if gradient:
                self.painter.setBrush(gradient)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(self.rect())

            # Отрисовка препятствий для player1 и player2
            for obstacle in self.obstacles1:
                if obstacle:
                    obstacle.draw(self.painter)
            for obstacle in self.obstacles2:
                if obstacle:
                    obstacle.draw(self.painter)

            # Рисуем трейлы
            self.draw_trail(self.painter, self.trail1, self.trail_start_color1, self.trail_end_color1)
            self.draw_trail(self.painter, self.trail2, self.trail_start_color2, self.trail_end_color2)

            # Рисуем разделитель
            separator_width = 50  # Ширина разделителя
            separator_x = self.width() // 2 - separator_width // 2  # Центр экрана
            separator_rect = QRect(separator_x, 0, separator_width, self.height())
            self.painter.fillRect(separator_rect, self.separator_brush)

            # Отрисовка света для игроков
            if self.player1.is_visible:
                self.player1.draw_light(self.painter)  # Отрисовка света для player1
            if self.player2.is_visible:
                self.player2.draw_light(self.painter)  # Отрисовка света для player2


            # Рисуем линии движения
            self.sepo.draw(self.painter, self.height())

            # Отображение FPS
            if self.show_fps:
                self.painter.setPen(QColor(255, 255, 255))
                fps_text = f"FPS: {self.fps:.1f}"
                self.painter.drawText(10, 30, fps_text)
            # Отображение пройденного пути для player1 (красный, верхний правый угол)
            self.painter.setFont(self.font)  # Определяем размер шрифта
            self.painter.setPen(self.trail_color2)  # Красный цвет трейла
            # Пройденное расстояние для player1
            text_player1 = f"Пройдено: {int(self.distance_traveled_player1)} м / {self.target_distance} м"
            text_width_player1 = self.painter.fontMetrics().width(text_player1)
            self.painter.drawText(self.width() - text_width_player1 - 20, 50, text_player1)
            # Скорость для player1
            speed_player1 = self.player1.get_current_speed()
            speed_text_player1 = f"Скорость: {speed_player1} м/с"
            speed_text_width_player1 = self.painter.fontMetrics().width(speed_text_player1)
            self.painter.drawText(self.width() - speed_text_width_player1 - 20, 80, speed_text_player1)
            # Отображение пройденного пути для player2 (синий, верхний левый угол)
            self.painter.setPen(self.trail_color1)  # Синий цвет трейла
            # Пройденное расстояние для player2
            text_player2 = f"Пройдено: {int(self.distance_traveled_player2)} м / {self.target_distance} м"
            self.painter.drawText(10, 50, text_player2)
            # Скорость для player2
            speed_player2 = self.player2.get_current_speed()
            speed_text_player2 = f"Скорость: {speed_player2} м/с"
            self.painter.drawText(10, 80, speed_text_player2)
            # Обновление прогресс-баров
            self.short_circuit_bar_player1.setValue(int(self.player1.get_short_circuit_level()))
            self.short_circuit_bar_player2.setValue(int(self.player2.get_short_circuit_level()))
        except Exception as e:
            print(f"Ошибка в paintEvent: {e}")
        finally:
            self.painter.end()

    def update_fps_visibility(self, visible):
        """Обновляет видимость FPS."""
        self.show_fps = visible
        self.update()  # Перерисовываем экран

    def draw_trail(self, painter, trail, start_color, end_color):
        for i, (x, y) in enumerate(trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length  # Коэффициент интерполяции
            from engine.game_logic import GameEngine
            interpolated_color = GameEngine.interpolate_color(start_color, end_color, factor) if hasattr(GameEngine,
                                                                                                         "interpolate_color") else start_color
            interpolated_color.setAlpha(max(0, alpha))  # Устанавливаем прозрачность
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
        self.distance_traveled_player1 = 0
        self.distance_traveled_player2 = 0
        self.timer.start(16)
        self.time_timer.start(self.day_night.tick_interval_ms)
        self.obstacle_spawn_timer1.start(2000)
        self.obstacle_spawn_timer2.start(2000)
        self.exposed_wire_spawn_timer1.start(3000)
        self.exposed_wire_spawn_timer2.start(3000)
        self.tower_spawn_timer1.start(8000)
        self.tower_spawn_timer2.start(8000)
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200
        self.short_circuit_bar_player1.setValue(0)
        self.short_circuit_bar_player2.setValue(0)
        self.trail1.clear()
        self.trail2.clear()
        self.obstacles1.clear()  # Препятствия для player1
        self.obstacles2.clear()  # Препятствия для player2
        self.transmission_towers1.clear()  # Опоры ЛЭП для player1
        self.transmission_towers2.clear()  # Опоры ЛЭП для player2
        self.exposed_wires1.clear()  # Оголенные провода для player1
        self.exposed_wires2.clear()  # Оголенные провода для player2

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
        self.distance_traveled_player1 = max(
            0,
            self.distance_traveled_player1 + meters_this_frame_player1 - self.player1.distance_penalty
        )
        self.distance_traveled_player2 = max(
            0,
            self.distance_traveled_player2 + meters_this_frame_player2 - self.player2.distance_penalty
        )

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
            obstacle.move(self.player1.get_current_speed())
        # Удаление препятствий, которые вышли за пределы экрана
        self.obstacles1 = [o for o in self.obstacles1 if not o.is_off_screen()]

        # Передвижение препятствий для player2
        for obstacle in self.obstacles2:
            obstacle.speed = self.player2.get_current_speed()  # Устанавливаем скорость препятствия равной скорости игрока
            obstacle.move(self.player2.get_current_speed())
        # Удаление препятствий, которые вышли за пределы экрана
        self.obstacles2 = [o for o in self.obstacles2 if not o.is_off_screen()]

        # Передвижение опор ЛЭП для player1
        for tower in self.transmission_towers1:
            tower.move(self.player2.get_current_speed())

        # Передвижение опор ЛЭП для player2
        for tower in self.transmission_towers2:
            tower.move(self.player1.get_current_speed())

        # Удаление ушедших за экран опор ЛЭП
        self.transmission_towers1 = [tower for tower in self.transmission_towers1 if not tower.is_off_screen()]
        self.transmission_towers2 = [tower for tower in self.transmission_towers2 if not tower.is_off_screen()]

        for wire in self.exposed_wires1:
            wire.move(self.player1.get_current_speed())
        for wire in self.exposed_wires2:
            wire.move(self.player2.get_current_speed())

        # Удаление ушедших за экран оголенных проводов
        self.exposed_wires1 = [wire for wire in self.exposed_wires1 if not wire.is_off_screen(540)]
        self.exposed_wires2 = [wire for wire in self.exposed_wires2 if not wire.is_off_screen(540)]

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

        # Обновление прогресс-баров
        short_circuit_level_player1 = self.player1.get_short_circuit_level()
        short_circuit_level_player2 = self.player2.get_short_circuit_level()
        self.short_circuit_bar_player1.setValue(int(short_circuit_level_player1))
        self.short_circuit_bar_player2.setValue(int(short_circuit_level_player2))

        # --- НОВЫЕ ВЫЗОВЫ ДЛЯ ОБНОВЛЕНИЯ ИЗОБРАЖЕНИЙ ---
        # Обновление изображений скорости и стадий КЗ для обоих игроков
        self.update_speed_images(self.player1, self.speed_images_player1)
        self.update_short_circuit_images(self.player1, self.short_circuit_images_player1)

        self.update_speed_images(self.player2, self.speed_images_player2)
        self.update_short_circuit_images(self.player2, self.short_circuit_images_player2)

        # Обновление интерфейса
        self.update()

    def update_trail(self, player, trail, current_trail_x, target_trail_x, color):
        current_speed = player.get_current_speed()  # Получаем текущую скорость игрока
        # Плавное обновление координаты X трейла
        if current_trail_x != target_trail_x:
            delta = target_trail_x - current_trail_x
            step = delta / self.trail_transition_speed
            current_trail_x += step
        # Добавление нескольких точек в трейл
        num_points = 1  # Количество точек зависит от скорости
        for i in range(num_points):
            factor = i / num_points  # Коэффициент интерполяции
            interpolated_x = int(current_trail_x + (target_trail_x - current_trail_x) * factor)
            y_offset = i * (current_speed // num_points)  # Смещение по Y для каждой точки
            trail.insert(0, (interpolated_x, player.y - y_offset))
        # Ограничение длины трейла
        while len(trail) > self.max_trail_length:
            trail.pop()
        # Сдвигаем все точки трейла вниз
        trail[:] = [(x, y + current_speed) for x, y in trail]
        return current_trail_x

    def check_collisions(self):
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
        player.apply_collision_penalty(penalty)  # Применяем штраф (откидываем на 20 метров)
        distance_traveled -= penalty  # Отбрасываем игрока назад
        player.enable_invincibility(5000)  # Включаем неуязвимость на 5 секунд
        player.short_circuit_level = 0  # Сбрасываем уровень КЗ до нуля
        player.current_speed_index = 0  # Сбрасываем скорость до минимальной (уровень 1)
        player.speed = player.speed_levels[player.current_speed_index]  # Обновляем текущую скорость

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
            self.is_game_over = False
            self.set_target_distance(self.target_distance)
        else:
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)
    def toggle_pause(self):
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True
        if self.is_paused:
            self.timer.stop()
            if self.parent:
                self.parent.main_menu.current_mode = "duo"
                self.parent.pause_menu.set_last_frame(self.grab())
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)