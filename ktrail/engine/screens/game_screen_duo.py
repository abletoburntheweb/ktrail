# engine/screens/game_screen_duo.py
from random import choice
from time import perf_counter
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient, QFont, QPixmap

from engine.player_duo import PlayerDuo
from engine.obstacle_duo import ObstacleDuo, PowerLineDuo, TransmissionTowerDuo, ExposedWireDuo, Seporator
from engine.day_night import DayNightSystem
from engine.powerups import SpeedBoostDuo
from engine.rotating_panel import RotatingPanel
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
        self.speed_to_meters_coefficient = 0.3
        self.speed = 10
        self.init_ui()

        self.frame_count = 0
        self.fps = 0
        self.last_fps_update_time = perf_counter()
        self.show_fps = True

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

        self.tile_manager.load_default_tile_types()

        self.tile_manager.init_tiles()

        self.player1 = PlayerDuo(player_id=1)
        self.player2 = PlayerDuo(player_id=2)

        self.power_line_duo = PowerLineDuo()

        self.sepo = Seporator()

        self.init_side_panels()

        self.max_trail_length = 20
        self.trail1 = []
        self.trail2 = []
        self.trail_width = 10
        self.trail_color1 = QColor("#4aa0fc")  # голубой
        self.trail_color2 = QColor("#ff6b6b")  # красный
        self.trail_transition_speed = 5

        self.current_trail_x1 = self.player1.x + 15
        self.target_trail_x1 = self.player1.x + 15

        self.current_trail_x2 = self.player2.x + 15
        self.target_trail_x2 = self.player2.x + 15

        self.obstacles1 = []
        self.obstacles2 = []
        self.transmission_towers1 = []
        self.transmission_towers2 = []
        self.exposed_wires1 = []
        self.exposed_wires2 = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.obstacle_spawn_timer1 = QTimer(self)
        self.obstacle_spawn_timer1.timeout.connect(self.spawn_obstacle1)
        self.obstacle_spawn_timer2 = QTimer(self)
        self.obstacle_spawn_timer2.timeout.connect(self.spawn_obstacle2)
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)

        self.tower_spawn_timer1 = QTimer(self)
        self.tower_spawn_timer1.timeout.connect(self.spawn_transmission_tower1)

        self.tower_spawn_timer2 = QTimer(self)
        self.tower_spawn_timer2.timeout.connect(self.spawn_transmission_tower2)

        self.exposed_wire_spawn_timer1 = QTimer(self)
        self.exposed_wire_spawn_timer1.timeout.connect(self.spawn_exposed_wire1)
        self.exposed_wire_spawn_timer2 = QTimer(self)
        self.exposed_wire_spawn_timer2.timeout.connect(self.spawn_exposed_wire2)

        self.active_powerups1 = []
        self.active_powerups2 = []
        self.powerup_spawn_timer1 = QTimer(self)
        self.powerup_spawn_timer1.timeout.connect(self.spawn_powerup1)
        self.powerup_spawn_timer2 = QTimer(self)
        self.powerup_spawn_timer2.timeout.connect(self.spawn_powerup2)
        self.is_game_over = False
        self.painter = QPainter()
        self.player1_brush = QBrush(Qt.red)
        self.player2_brush = QBrush(Qt.blue)
        self.obstacle_brush = QBrush(Qt.black)
        self.street_lamp_brush = QBrush(Qt.darkGray)
        self.separator_brush = QBrush(QColor(128, 128, 128))
        self.trail_start_color1 = QColor("#ff6b6b")
        self.trail_end_color1 = QColor("#FFFFFF")
        self.trail_start_color2 = QColor("#4aa0fc")
        self.trail_end_color2 = QColor("#FFFFFF")
        self.font = QFont("Arial", 20)
        self.light_gradient = QRadialGradient()

    def init_ui(self):
        self.setWindowTitle("Дуо режим")
        self.setFixedSize(1920, 1080)

    def init_side_panels(self):
        self.setFixedSize(1920, 1080)

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

        self.side_panel_container = QWidget(self)
        self.side_panel_container.setGeometry(
            self.width() - right_panel_pixmap.width(),
            0,
            right_panel_pixmap.width(),
            right_panel_pixmap.height()
        )
        self.side_panel_container.setStyleSheet("background-color: transparent;")
        self.side_panel_container.raise_()

        self.side_panel_left_container = QWidget(self)
        self.side_panel_left_container.setGeometry(
            0,
            0,
            left_panel_pixmap.width(),
            left_panel_pixmap.height()
        )
        self.side_panel_left_container.setStyleSheet("background-color: transparent;")
        self.side_panel_left_container.raise_()

        self.speed_images_player1 = []
        self.short_circuit_images_player1 = []
        self.speed_images_player2 = []
        self.short_circuit_images_player2 = []

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

        self.create_speed_labels(self.speed_rect_right, self.short_circuit_rect_right, is_right=True)

        self.create_speed_labels(self.speed_rect_left, self.short_circuit_rect_left, is_right=False)

        self.distance_label_player1 = QLabel("0", self.side_panel_container)
        self.distance_label_player1.setAlignment(Qt.AlignCenter)
        self.distance_label_player1.setStyleSheet("""
            color: #992F00; 
            font-family: Consolas;  
            font-size: 72px; 
            font-weight: bold;  
        """)
        self.distance_label_player1.setGeometry(330, 10, 200, 100)

        self.distance_label_player2 = QLabel("0", self.side_panel_left_container)
        self.distance_label_player2.setAlignment(Qt.AlignCenter)
        self.distance_label_player2.setStyleSheet("""
            color: #2C3F8C;  
            font-family: Consolas;  
            font-size: 72px; 
            font-weight: bold;  
        """)
        self.distance_label_player2.setGeometry(100, 10, 200, 100)

    def create_speed_labels(self, speed_rect, short_circuit_rect, is_right):
        """Создание виджетов для отображения скорости и КЗ."""
        container = self.side_panel_container if is_right else self.side_panel_left_container

        for _ in range(4):
            image_path = "assets/textures/speed.png" if is_right else "assets/textures/speed2.png"
            labels = self.speed_images_player1 if is_right else self.speed_images_player2
            self.add_speed_image(labels, container, speed_rect)

        for i in range(3):
            image_path = f"assets/textures/{['f', 's', 't'][i]}_stage.png" if is_right else f"assets/textures/{['f', 's', 't'][i]}_stage2.png"
            labels = self.short_circuit_images_player1 if is_right else self.short_circuit_images_player2
            self.add_short_circuit_image(image_path, labels, container, short_circuit_rect)

    def add_speed_image(self, labels, container, rect):
        if len(labels) >= 4:
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
        speed_image_label.hide()
        labels.append(speed_image_label)

    def add_short_circuit_image(self, image_path, labels, container, rect):
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
        short_circuit_image_label.hide()
        labels.append(short_circuit_image_label)

    def toggle_green_stage(self, activate, player_id):
        if player_id == 1:
            container = self.side_panel_container
        elif player_id == 2:
            container = self.side_panel_left_container

        if activate:
            if player_id == 1:
                if not hasattr(self, "green_stage_label_player1") or self.green_stage_label_player1 is None:
                    self.green_stage_label_player1 = QLabel(container)
                    green_stage_pixmap = QPixmap("assets/textures/green_stage.png")
                    self.green_stage_label_player1.setPixmap(green_stage_pixmap)
                    self.green_stage_label_player1.setScaledContents(False)
                    image_width = green_stage_pixmap.width()
                    image_height = green_stage_pixmap.height()
                    self.green_stage_label_player1.setGeometry(195, 20, image_width, image_height)
                self.green_stage_label_player1.show()
                self.green_stage_label_player1.raise_()
            elif player_id == 2:
                if not hasattr(self, "green_stage_label_player2") or self.green_stage_label_player2 is None:
                    self.green_stage_label_player2 = QLabel(container)
                    green_stage_pixmap = QPixmap("assets/textures/green_stage2.png")
                    self.green_stage_label_player2.setPixmap(green_stage_pixmap)
                    self.green_stage_label_player2.setScaledContents(False)
                    image_width = green_stage_pixmap.width()
                    image_height = green_stage_pixmap.height()
                    self.green_stage_label_player2.setGeometry(380, 20, image_width, image_height)
                self.green_stage_label_player2.show()
                self.green_stage_label_player2.raise_()
        else:
            if player_id == 1:
                if hasattr(self, "green_stage_label_player1") and self.green_stage_label_player1 is not None:
                    self.green_stage_label_player1.hide()
                    self.green_stage_label_player1.deleteLater()
                    self.green_stage_label_player1 = None
            elif player_id == 2:
                if hasattr(self, "green_stage_label_player2") and self.green_stage_label_player2 is not None:
                    self.green_stage_label_player2.hide()
                    self.green_stage_label_player2.deleteLater()
                    self.green_stage_label_player2 = None

    def remove_speed_image(self, labels):
        if not labels:
            return
        last_label = labels.pop()
        last_label.deleteLater()

    def remove_short_circuit_image(self, labels):
        if not labels:
            return
        last_label = labels.pop()
        last_label.deleteLater()

    def update_speed_images(self, player, speed_images):
        current_speed_level = player.get_current_speed_level()
        for i, image in enumerate(speed_images):
            if i < current_speed_level - 1:
                image.show()
            else:
                image.hide()

    def update_distance_labels(self):
        text_player1 = f"{int(self.distance_traveled_player1)}"
        self.distance_label_player1.setText(text_player1)

        text_player2 = f"{int(self.distance_traveled_player2)}"
        self.distance_label_player2.setText(text_player2)
    def update_short_circuit_images(self, player, short_circuit_images):
        short_circuit_level = player.get_short_circuit_level()
        if short_circuit_level >= 40 and short_circuit_level < 60:
            short_circuit_images[0].show()
            short_circuit_images[1].hide()
            short_circuit_images[2].hide()
        elif short_circuit_level >= 60 and short_circuit_level < 80:
            short_circuit_images[0].show()
            short_circuit_images[1].show()
            short_circuit_images[2].hide()
        elif short_circuit_level >= 80:
            short_circuit_images[0].show()
            short_circuit_images[1].show()
            short_circuit_images[2].show()
        else:
            for image in short_circuit_images:
                image.hide()
    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_obstacle1(self):
        MAX_OBSTACLES_PER_PLAYER = 20
        if not self.is_game_over and len(self.obstacles1) < MAX_OBSTACLES_PER_PLAYER:
            obstacle = ObstacleDuo()
            obstacle.x = choice([1313, 1567, 1807])
            self.obstacles1.append(obstacle)

    def spawn_obstacle2(self):
        MAX_OBSTACLES_PER_PLAYER = 20
        if not self.is_game_over and len(self.obstacles2) < MAX_OBSTACLES_PER_PLAYER:
            obstacle = ObstacleDuo()
            obstacle.x = choice([73, 327, 567])
            self.obstacles2.append(obstacle)

    def spawn_exposed_wire1(self):
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([1313, 1567, 1807])
            self.exposed_wires1.append(wire)

    def spawn_exposed_wire2(self):
        if not self.is_game_over:
            wire = ExposedWireDuo(self.width(), self.height())
            wire.x = choice([73, 327, 567])
            self.exposed_wires2.append(wire)

    def spawn_transmission_tower1(self):
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = 40
            self.transmission_towers1.append(tower)

    def spawn_transmission_tower2(self):
        if not self.is_game_over:
            tower = TransmissionTowerDuo(screen_height=self.height())
            tower.x = 1280
            self.transmission_towers2.append(tower)

    def spawn_powerup1(self):
        if not self.is_game_over:
            powerup = SpeedBoostDuo(screen_width=self.width(), screen_height=self.height(), side="right")
            self.active_powerups1.append(powerup)

    def spawn_powerup2(self):
        if not self.is_game_over:
            powerup = SpeedBoostDuo(screen_width=self.width(), screen_height=self.height(), side="left")
            self.active_powerups2.append(powerup)


    def paintEvent(self, event):
        try:
            self.painter.begin(self)

            self.tile_manager.draw_tiles(self.painter)

            for tower in self.transmission_towers1:
                if tower:
                    tower.draw(self.painter)

            for tower in self.transmission_towers2:
                if tower:
                    tower.draw(self.painter)

            self.power_line_duo.draw(self.painter, self.height())

            for wire in self.exposed_wires1:
                if wire:
                    wire.draw(self.painter)
            for wire in self.exposed_wires2:
                if wire:
                    wire.draw(self.painter)

            for powerup in self.active_powerups1:
                if powerup:
                    powerup.draw(self.painter)

            for powerup in self.active_powerups2:
                if powerup:
                    powerup.draw(self.painter)

            gradient = self.day_night.get_background_gradient(self.height())
            if gradient:
                self.painter.setBrush(gradient)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(self.rect())

            for obstacle in self.obstacles1:
                if obstacle:
                    obstacle.draw(self.painter)
            for obstacle in self.obstacles2:
                if obstacle:
                    obstacle.draw(self.painter)

            self.draw_trail(self.painter, self.trail1, self.trail_start_color1, self.trail_end_color1)
            self.draw_trail(self.painter, self.trail2, self.trail_start_color2, self.trail_end_color2)

            separator_width = 50
            separator_x = self.width() // 2 - separator_width // 2
            separator_rect = QRect(separator_x, 0, separator_width, self.height())
            self.painter.fillRect(separator_rect, self.separator_brush)

            if self.player1.is_visible:
                self.player1.draw_light(self.painter)
            if self.player2.is_visible:
                self.player2.draw_light(self.painter)


            self.sepo.draw(self.painter, self.height())


        except Exception as e:
            print(f"Ошибка в paintEvent: {e}")
        finally:
            self.painter.end()

    def draw_trail(self, painter, trail, start_color, end_color):
        for i, (x, y) in enumerate(trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length
            from engine.game_logic import GameEngine
            interpolated_color = GameEngine.interpolate_color(start_color, end_color, factor) if hasattr(GameEngine,
                                                                                                         "interpolate_color") else start_color
            interpolated_color.setAlpha(max(0, alpha))
            painter.fillRect(x, y, self.trail_width, self.trail_width, QBrush(interpolated_color))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggle_pause()
        else:
            self.player1.move(event.key())
            self.player2.move(event.key())
            self.target_trail_x1 = self.player1.x + 15
            self.target_trail_x2 = self.player2.x + 15
            if event.key() in [Qt.Key_Up, Qt.Key_Down]:
                self.player1.change_speed(event.key())
            if event.key() in [Qt.Key_W, Qt.Key_S]:
                self.player2.change_speed(event.key())

    def set_target_distance(self, distance):
        self.is_game_over = False
        self.target_distance = distance
        self.distance_traveled_player1 = 0
        self.distance_traveled_player2 = 0
        self.timer.start(12)
        self.time_timer.start(self.day_night.tick_interval_ms)
        self.obstacle_spawn_timer1.start(2000)
        self.obstacle_spawn_timer2.start(2000)
        self.exposed_wire_spawn_timer1.start(3000)
        self.exposed_wire_spawn_timer2.start(3000)
        self.tower_spawn_timer1.start(8000)
        self.tower_spawn_timer2.start(8000)
        self.powerup_spawn_timer1.start(15000)
        self.powerup_spawn_timer2.start(15000)
        self.tile_manager.init_tiles()
        self.day_night.current_tick = 8200
        self.trail1.clear()
        self.trail2.clear()
        self.obstacles1.clear()
        self.obstacles2.clear()
        self.transmission_towers1.clear()
        self.transmission_towers2.clear()
        self.exposed_wires1.clear()
        self.exposed_wires2.clear()
        self.active_powerups1.clear()
        self.active_powerups2.clear()

    def update_game(self):
        try:
            if self.is_game_over:
                return

            speed_player1 = self.player1.get_current_speed()
            speed_player2 = self.player2.get_current_speed()

            meters_this_frame_player1 = speed_player1 * self.speed_to_meters_coefficient
            meters_this_frame_player2 = speed_player2 * self.speed_to_meters_coefficient

            self.update_distance_labels()

            self.distance_traveled_player1 = max(
                0,
                self.distance_traveled_player1 + meters_this_frame_player1 - self.player1.distance_penalty
            )
            self.distance_traveled_player2 = max(
                0,
                self.distance_traveled_player2 + meters_this_frame_player2 - self.player2.distance_penalty
            )

            self.player1.distance_penalty = 0
            self.player2.distance_penalty = 0

            if self.distance_traveled_player1 >= self.target_distance and self.distance_traveled_player2 < self.target_distance:
                self.show_victory(winner="Игрок 1")
                return
            elif self.distance_traveled_player2 >= self.target_distance and self.distance_traveled_player1 < self.target_distance:
                self.show_victory(winner="Игрок 2")
                return
            elif self.distance_traveled_player1 >= self.target_distance and self.distance_traveled_player2 >= self.target_distance:
                self.show_draw()
                return

            self.current_trail_x1 = self.update_trail(
                self.player1, self.trail1, self.current_trail_x1, self.target_trail_x1, self.trail_color1
            )
            self.current_trail_x2 = self.update_trail(
                self.player2, self.trail2, self.current_trail_x2, self.target_trail_x2, self.trail_color2
            )

            for obstacle in self.obstacles1:
                obstacle.speed = self.player1.get_current_speed()
                obstacle.move(self.player1.get_current_speed())
            self.obstacles1 = [o for o in self.obstacles1 if not o.is_off_screen()]

            for obstacle in self.obstacles2:
                obstacle.speed = self.player2.get_current_speed()
                obstacle.move(self.player2.get_current_speed())
            self.obstacles2 = [o for o in self.obstacles2 if not o.is_off_screen()]

            for tower in self.transmission_towers1:
                tower.move(self.player2.get_current_speed())

            for tower in self.transmission_towers2:
                tower.move(self.player1.get_current_speed())

            self.transmission_towers1 = [tower for tower in self.transmission_towers1 if not tower.is_off_screen()]
            self.transmission_towers2 = [tower for tower in self.transmission_towers2 if not tower.is_off_screen()]

            for wire in self.exposed_wires1:
                wire.move(self.player1.get_current_speed())
            for wire in self.exposed_wires2:
                wire.move(self.player2.get_current_speed())

            self.exposed_wires1 = [wire for wire in self.exposed_wires1 if not wire.is_off_screen(1200)]
            self.exposed_wires2 = [wire for wire in self.exposed_wires2 if not wire.is_off_screen(1200)]

            for powerup in self.active_powerups1[:]:
                if powerup:
                    powerup.move(self.player1.speed)

                    if self.player1.get_rect().intersects(powerup.get_rect()):
                        powerup.activate(self.player1, self)
                        self.active_powerups1.remove(powerup)

            self.active_powerups1 = [pu for pu in self.active_powerups1 if pu and not pu.is_off_screen(self.height())]

            for powerup in self.active_powerups2[:]:
                if powerup:
                    powerup.move(self.player2.speed)

                    if self.player2.get_rect().intersects(powerup.get_rect()):
                        powerup.activate(self.player2, self)
                        self.active_powerups2.remove(powerup)

            self.active_powerups2 = [pu for pu in self.active_powerups2 if pu and not pu.is_off_screen(self.height())]

            self.check_collisions()

            self.tile_manager.update_tiles(speed_player1, speed_player2)

            self.frame_count += 1
            current_time = perf_counter()
            elapsed_time = current_time - self.last_fps_update_time
            if elapsed_time >= 1.0:
                self.fps = self.frame_count / elapsed_time
                self.frame_count = 0
                self.last_fps_update_time = current_time

            self.update_speed_images(self.player1, self.speed_images_player1)
            self.update_short_circuit_images(self.player1, self.short_circuit_images_player1)

            self.update_speed_images(self.player2, self.speed_images_player2)
            self.update_short_circuit_images(self.player2, self.short_circuit_images_player2)

            self.update()
        except Exception as e:
            print(f"Ошибка в update_game: {e}")

    def update_trail(self, player, trail, current_trail_x, target_trail_x, color):
        current_speed = player.get_current_speed()
        if current_trail_x != target_trail_x:
            delta = target_trail_x - current_trail_x
            step = delta / self.trail_transition_speed
            current_trail_x += step
        num_points = 1
        for i in range(num_points):
            factor = i / num_points
            interpolated_x = int(current_trail_x + (target_trail_x - current_trail_x) * factor)
            y_offset = i * (current_speed // num_points)
            trail.insert(0, (interpolated_x, player.y - y_offset))
        while len(trail) > self.max_trail_length:
            trail.pop()
        trail[:] = [(x, y + current_speed) for x, y in trail]
        return current_trail_x

    def check_collisions(self):
        p1_rect = self.player1.get_rect()
        p2_rect = self.player2.get_rect()

        if self.player1.get_short_circuit_level() >= self.player1.short_circuit_max:
            self.handle_collision(self.player1, self.distance_traveled_player1, 20)
            return

        if self.player2.get_short_circuit_level() >= self.player2.short_circuit_max:
            self.handle_collision(self.player2, self.distance_traveled_player2, 20)
            return

        for obstacle in self.obstacles1[:]:
            rect = obstacle.get_rect()
            if p1_rect.intersects(rect) and not self.player1.is_invincible:
                self.handle_collision(self.player1, self.distance_traveled_player1, 20)
                self.obstacles1.remove(obstacle)
                break

        for wire in self.exposed_wires1[:]:
            rect = wire.get_rect()
            if p1_rect.intersects(rect) and not self.player1.is_invincible:
                self.handle_collision(self.player1, self.distance_traveled_player1, 20)
                self.exposed_wires1.remove(wire)
                break

        for obstacle in self.obstacles2[:]:
            rect = obstacle.get_rect()
            if p2_rect.intersects(rect) and not self.player2.is_invincible:
                self.handle_collision(self.player2, self.distance_traveled_player2, 20)
                self.obstacles2.remove(obstacle)
                break

        for wire in self.exposed_wires2[:]:
            rect = wire.get_rect()
            if p2_rect.intersects(rect) and not self.player2.is_invincible:
                self.handle_collision(self.player2, self.distance_traveled_player2, 20)
                self.exposed_wires2.remove(wire)
                break

    def handle_collision(self, player, distance_traveled, penalty):
        if player.is_speed_boost_active:
            print("Столкновение во время SpeedBoost: деактивация и сброс скорости.")

            if player.player_id == 1:
                if hasattr(self, "green_stage_label_player1") and self.green_stage_label_player1:
                    self.green_stage_label_player1.hide()
                    self.green_stage_label_player1.deleteLater()
                    self.green_stage_label_player1 = None
            elif player.player_id == 2:
                if hasattr(self, "green_stage_label_player2") and self.green_stage_label_player2:
                    self.green_stage_label_player2.hide()
                    self.green_stage_label_player2.deleteLater()
                    self.green_stage_label_player2 = None

            for powerup in self.active_powerups1[:] if player == self.player1 else self.active_powerups2[:]:
                if isinstance(powerup, SpeedBoostDuo) and powerup.is_active:
                    powerup.deactivate(player, self)
                    break

            player.speed_levels = player.original_speed_levels or [10, 15, 20, 25, 30]
            player.current_speed_index = player.original_current_speed_index or 2
            player.speed = player.speed_levels[player.current_speed_index]
            player.can_change_speed = True
            player.is_speed_boost_active = False

        player.apply_collision_penalty(penalty)
        distance_traveled -= penalty
        player.enable_invincibility(5000)
        player.short_circuit_level = 0
        player.current_speed_index = 0
        player.speed = player.speed_levels[player.current_speed_index]

    def show_victory(self, winner=""):
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
            self.is_game_over = False
            self.set_target_distance(self.target_distance)
            if self.parent:
                self.parent.play_music(self.parent.game_music_path)
            self.update()
        else:
            if self.parent:
                self.parent.stop_music()
                self.parent.play_music(self.parent.menu_music_path)
                QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
                QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
                QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())

    def show_draw(self):
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer1.stop()
        self.obstacle_spawn_timer2.stop()
        self.tower_spawn_timer1.stop()
        self.tower_spawn_timer2.stop()
        self.exposed_wire_spawn_timer1.stop()
        self.exposed_wire_spawn_timer2.stop()
        self.powerup_spawn_timer1.stop()
        self.powerup_spawn_timer2.stop()
        self.time_timer.stop()

        msg = QMessageBox()
        msg.setWindowTitle("Ничья!")
        msg.setText("Оба игрока достигли финиша одновременно!")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Information)
        choice = msg.exec_()

        if choice == QMessageBox.Retry:
            self.is_game_over = False
            self.set_target_distance(self.target_distance)
            if self.parent:
                self.parent.play_music(self.parent.game_music_path)
            self.update()
        else:
            if self.parent:
                self.parent.stop_music()
                self.parent.play_music(self.parent.menu_music_path)
                QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
                QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
                QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())

    def toggle_pause(self):
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True

        if self.is_paused:
            self.timer.stop()
            self.obstacle_spawn_timer1.stop()
            self.obstacle_spawn_timer2.stop()
            self.tower_spawn_timer1.stop()
            self.tower_spawn_timer2.stop()
            self.exposed_wire_spawn_timer1.stop()
            self.exposed_wire_spawn_timer2.stop()
            self.powerup_spawn_timer1.stop()
            self.powerup_spawn_timer2.stop()
            self.time_timer.stop()

            self.player1.pause_short_circuit_level()
            self.player2.pause_short_circuit_level()

            self.last_frame_pixmap = self.grab()

            if self.parent:
                self.parent.main_menu.current_mode = "duo"
                self.parent.pause_menu.set_last_frame(self.last_frame_pixmap)
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)
            self.obstacle_spawn_timer1.start(2000)
            self.obstacle_spawn_timer2.start(2000)
            self.tower_spawn_timer1.start(8000)
            self.tower_spawn_timer2.start(8000)
            self.exposed_wire_spawn_timer1.start(3000)
            self.exposed_wire_spawn_timer2.start(3000)
            self.powerup_spawn_timer1.start(15000)
            self.powerup_spawn_timer2.start(15000)
            self.time_timer.start(self.day_night.tick_interval_ms)

            self.player1.resume_short_circuit_level()
            self.player2.resume_short_circuit_level()