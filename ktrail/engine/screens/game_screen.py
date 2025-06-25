import json
from time import perf_counter
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QRadialGradient
from engine.car import Car
from engine.day_night import DayNightSystem
from engine.player import Player
from engine.obstacle import Obstacle, PowerLine, ExposedWire, TransmissionTower
from engine.powerups import SpeedBoost
from engine.tile_manager import TileManager

from engine.rotating_panel import RotatingPanel


class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.start_time = None
        self.elapsed_time = 0
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update_time = perf_counter()
        self.show_fps = self.parent.settings.get("show_fps", True)

        self.day_night = DayNightSystem()
        self.target_distance = 0
        self.distance_traveled = 0
        self.speed_to_meters_coefficient = 0.3
        self.speed = 10
        self.side_panel_label = QLabel(self)
        self.side_panel_pixmap = QPixmap("assets/textures/side_panel.png")
        self.side_panel_label.setPixmap(self.side_panel_pixmap)
        self.side_panel_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.side_panel_label.setScaledContents(True)

        self.init_ui()

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
        self.tile_manager.load_default_tile_types()

        self.tile_manager.init_tiles()

        self.player = Player()

        self.transmission_towers = []

        self.tower_spawn_timer = QTimer(self)
        self.tower_spawn_timer.timeout.connect(self.spawn_transmission_tower)

        self.obstacles = []
        self.obstacle_spawn_timer = QTimer(self)
        self.obstacle_spawn_timer.timeout.connect(self.spawn_obstacle)
        self.cars = []
        self.car_spawn_timer = QTimer(self)
        self.car_spawn_timer.timeout.connect(self.spawn_car)
        self.exposed_wires = []

        self.exposed_wire_spawn_timer = QTimer(self)
        self.exposed_wire_spawn_timer.timeout.connect(self.spawn_exposed_wire)
        self.active_powerups = []

        self.powerup_spawn_timer = QTimer(self)
        self.powerup_spawn_timer.timeout.connect(self.spawn_powerup)

        self.power_line = PowerLine()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)

        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_day_night)

        self.is_game_over = False
        self.total_removed_obstacles = 0

        self.painter = QPainter()

        side_panel_width = self.side_panel_pixmap.width()
        side_panel_height = self.side_panel_pixmap.height()
        self.side_panel_label.setFixedSize(side_panel_width, side_panel_height)
        self.side_panel_label.setGeometry(
            self.width() - side_panel_width,
            0,
            side_panel_width,
            side_panel_height
        )

        self.side_panel_container = QWidget(self)
        self.side_panel_container.setGeometry(
            self.width() - side_panel_width,
            0,
            side_panel_width,
            side_panel_height
        )
        self.side_panel_container.setStyleSheet("background-color: transparent;")
        self.side_panel_container.raise_()

        self.distance_label = QLabel("200", self.side_panel_container)
        self.distance_label.setAlignment(Qt.AlignCenter)
        self.distance_label.setStyleSheet("""
            color: #B29400; 
            font-family: Consolas;  
            font-size: 72px; 
            font-weight: bold;  
        """)
        self.distance_label.setGeometry(330, 10, 200, 100)

        self.time_label = QLabel("30", self.side_panel_container)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #B29400; 
            font-family: Consolas;  
            font-size: 64px; 
            font-weight: bold; 
        """)
        self.time_label.setGeometry(175, 205, 200, 100)

        self.short_circuit_rect = {
            'x': 95,
            'y': 60,
            'width': 60,
            'height': 70
        }
        self.short_circuit_labels = []

        self.speed_image_labels = []

        self.show()

    def init_ui(self):
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def update_day_night(self):
        self.day_night.update_time()
        self.update()

    def spawn_transmission_tower(self):
        if not self.is_game_over:
            tower = TransmissionTower(screen_height=self.height())
            self.transmission_towers.append(tower)

    def spawn_obstacle(self):
        if not self.is_game_over:
            obstacle = Obstacle(self.width(), self.height())
            self.obstacles.append(obstacle)

    def spawn_exposed_wire(self):
        if not self.is_game_over:
            exposed_wire = ExposedWire(self.width(), self.height())
            self.exposed_wires.append(exposed_wire)

    def spawn_car(self):
        if not self.is_game_over:
            car = Car(self.width(), self.height())
            self.cars.append(car)

    def spawn_powerup(self):
        if not self.is_game_over:
            powerup = SpeedBoost(screen_width=self.width(), screen_height=self.height())
            self.active_powerups.append(powerup)

    def update_distance_text(self, distance_traveled, target_distance):
        text = f"{int(distance_traveled)}"
        self.distance_label.setText(text)

    def update_time_text(self, elapsed_time):
        time_text = f"{elapsed_time:.1f}"
        self.time_label.setText(time_text)

    def update_short_circuit_images(self, progress):
        for label in self.short_circuit_labels:
            label.deleteLater()
        self.short_circuit_labels.clear()

        if progress >= 40 and progress < 60:
            self.add_short_circuit_image("assets/textures/f_stage.png")
        elif progress >= 60 and progress < 80:
            self.add_short_circuit_image("assets/textures/f_stage.png")
            self.add_short_circuit_image("assets/textures/s_stage.png")
        elif progress >= 80:
            self.add_short_circuit_image("assets/textures/f_stage.png")
            self.add_short_circuit_image("assets/textures/s_stage.png")
            self.add_short_circuit_image("assets/textures/t_stage.png")

    def add_speed_image(self):
        if len(self.speed_image_labels) >= 4:
            return

        speed_image_label = QLabel(self.side_panel_container)
        speed_image_pixmap = QPixmap("assets/textures/speed.png")
        speed_image_label.setPixmap(speed_image_pixmap)
        speed_image_label.setScaledContents(False)

        image_width = speed_image_pixmap.width()
        image_height = speed_image_pixmap.height()

        if len(self.speed_image_labels) == 0:
            y_position = 80
        else:
            last_label = self.speed_image_labels[-1]
            y_position = last_label.y() - image_height

        speed_image_label.setGeometry(195, y_position, image_width, image_height)

        self.speed_image_labels.append(speed_image_label)

        speed_image_label.show()
    def add_short_circuit_image(self, image_path):
        short_circuit_image_label = QLabel(self.side_panel_container)
        short_circuit_image_pixmap = QPixmap(image_path)
        short_circuit_image_label.setPixmap(short_circuit_image_pixmap)
        short_circuit_image_label.setScaledContents(False)

        image_width = short_circuit_image_pixmap.width()
        image_height = short_circuit_image_pixmap.height()

        base_x = self.short_circuit_rect['x']
        base_y = self.short_circuit_rect['y']

        if len(self.short_circuit_labels) == 0:
            y_position = base_y
        else:
            last_label = self.short_circuit_labels[-1]
            y_position = last_label.y() - image_height

        short_circuit_image_label.setGeometry(
            base_x,
            y_position,
            image_width,
            image_height
        )

        self.short_circuit_labels.append(short_circuit_image_label)
        short_circuit_image_label.show()

    def toggle_green_stage(self, activate):
        if activate:
            if not hasattr(self, "green_stage_label") or self.green_stage_label is None:
                self.green_stage_label = QLabel(self.side_panel_container)
                green_stage_pixmap = QPixmap("assets/textures/green_stage.png")
                self.green_stage_label.setPixmap(green_stage_pixmap)
                self.green_stage_label.setScaledContents(False)

                image_width = green_stage_pixmap.width()
                image_height = green_stage_pixmap.height()

                self.green_stage_label.setGeometry(195, 20, image_width, image_height)
                self.green_stage_label.show()
        else:
            if hasattr(self, "green_stage_label") and self.green_stage_label is not None:
                self.green_stage_label.hide()
                self.green_stage_label.deleteLater()
                self.green_stage_label = None

    def remove_speed_image(self):
        if not self.speed_image_labels:
            return
        last_label = self.speed_image_labels.pop()
        last_label.deleteLater()

        if hasattr(self, "green_stage_label") and self.green_stage_label is not None:
            current_y = 20
            for label in self.speed_image_labels:
                current_y -= label.height()
            self.green_stage_label.move(195, current_y)

    def paintEvent(self, event):
        try:
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.Antialiasing, True)

            # 1. Рисуем тайлы
            self.tile_manager.draw_tiles(self.painter)

            # 2. Отрисовка машин
            for car in self.cars:
                car.draw(self.painter)

            for tower in self.transmission_towers:
                if tower:
                    tower.draw(self.painter)

            # 3. Отрисовка линий ЛЭП
            self.power_line.draw(self.painter, self.height())

            # 5. Отрисовка паверапов
            for powerup in self.active_powerups:
                if powerup:
                    powerup.draw(self.painter)


            # 6. Накладываем градиент дня/ночи
            gradient = self.day_night.get_background_gradient(self.height())
            if gradient:
                self.painter.setBrush(gradient)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(self.rect())


            # 4. Отрисовка оголенных проводов с текстурой
            for exposed_wire in self.exposed_wires:
                if exposed_wire:
                    exposed_wire.draw(self.painter)

            # 7. Отрисовка препятствий с текстурой
            for obstacle in self.obstacles:
                if obstacle:
                    obstacle.draw(self.painter)

            # 8. Отрисовка трейла игрока
            self.player.draw_trail(self.painter)

            # 9. Отрисовка игрока
            if self.player:
                self.player.draw_player_light(self.painter)

            # 10. Отображение текста
            if self.target_distance > 0:
                text = f"Пройдено: {int(self.distance_traveled)} м / {self.target_distance} м"
                text_width = self.painter.fontMetrics().width(text)
                self.painter.setPen(QColor(255, 255, 255))
                self.painter.drawText(self.width() - text_width - 20, 50, text)

            speed_text = f"Скорость: {self.player.get_current_speed()} м/с"
            self.painter.drawText(10, 30, speed_text)

            if self.show_fps:
                fps_text = f"FPS: {self.fps:.1f}"
                self.painter.drawText(10, 60, fps_text)

            timer_text = f"Время: {self.elapsed_time:.1f} сек"
            self.painter.drawText(10, 90, timer_text)


        except Exception as e:
            print(f"Ошибка в paintEvent: {e}")
        finally:
            self.painter.end()

    def update_fps_visibility(self, visible):
        self.show_fps = visible
        self.update()

    def keyPressEvent(self, event):
        scan = event.nativeScanCode()

        SC_ESCAPE = 1
        SC_TILDE = 41
        SC_LEFT = 30
        SC_RIGHT = 32
        SC_UP = 17
        SC_DOWN = 31

        if scan == SC_ESCAPE:
            self.toggle_pause()

        elif scan == SC_TILDE:
            if self.parent:
                if self.parent.debug_menu.isVisible():
                    self.parent.debug_menu.hide()
                else:
                    self.parent.debug_menu.update_debug_info(self.day_night)
                    self.parent.debug_menu.show()
                    self.parent.debug_menu.raise_()
                    self.parent.debug_menu.setFocus()

        elif scan == SC_LEFT:
            self.player.move(Qt.Key_A)
            self.target_trail_x = self.player.x + 15

        elif scan == SC_RIGHT:
            self.player.move(Qt.Key_D)
            self.target_trail_x = self.player.x + 15

        elif scan == SC_UP:
            self.player.change_speed(Qt.Key_W)

        elif scan == SC_DOWN:
            self.player.change_speed(Qt.Key_S)

    def set_target_distance(self, distance):
        self.is_game_over = False
        self.target_distance = distance
        self.distance_traveled = 0
        self.start_time = perf_counter()
        self.elapsed_time = 0
        self.player = Player()
        self.obstacles.clear()
        self.cars.clear()
        self.exposed_wires.clear()
        self.transmission_towers.clear()
        self.tile_manager.init_tiles()
        self.timer.start(14)
        self.obstacle_spawn_timer.start(2000)
        self.car_spawn_timer.start(5000)
        self.tower_spawn_timer.start(8000)
        self.car_spawn_timer.start(5000)
        self.exposed_wire_spawn_timer.start(3000)
        self.powerup_spawn_timer.start(15000)
        self.time_timer.start(self.day_night.tick_interval_ms)

    def update_game(self):
        if self.is_game_over:
            return

        self.frame_count += 1
        current_time = perf_counter()
        elapsed_time_fps = current_time - self.last_fps_update_time
        if elapsed_time_fps >= 1.0:
            self.fps = self.frame_count / elapsed_time_fps
            self.frame_count = 0
            self.last_fps_update_time = current_time

        if self.start_time is not None:
            self.elapsed_time = current_time - self.start_time

        meters_this_frame = 0
        current_speed = self.player.get_current_speed()
        if current_speed is not None:
            meters_this_frame = current_speed * self.speed_to_meters_coefficient
        self.distance_traveled += meters_this_frame

        if self.distance_traveled >= self.target_distance:
            self.show_victory()
            return

        self.update_distance_text(self.distance_traveled, self.target_distance)

        self.player.update_trail(self.player.speed)

        self.update_time_text(self.elapsed_time)

        short_circuit_level = self.player.get_short_circuit_level()
        self.update_short_circuit_images(short_circuit_level)

        current_speed_level = self.player.get_current_speed_level()
        current_image_count = len(self.speed_image_labels)

        while current_image_count < current_speed_level - 1:
            self.add_speed_image()
            current_image_count += 1

        while current_image_count > current_speed_level - 1:
            self.remove_speed_image()
            current_image_count -= 1

        for obstacle in self.obstacles:
            obstacle.move(self.player.speed)

        for tower in self.transmission_towers:
            tower.move(self.player.speed)

        initial_count = len(self.transmission_towers)
        self.transmission_towers = [tower for tower in self.transmission_towers if not tower.is_off_screen(1200)]
        self.total_removed_obstacles += initial_count - len(self.transmission_towers)

        initial_count = len(self.obstacles)
        self.obstacles = [obstacle for obstacle in self.obstacles if not obstacle.is_off_screen(1200)]
        self.total_removed_obstacles += initial_count - len(self.obstacles)

        for exposed_wire in self.exposed_wires:
            exposed_wire.move(self.player.speed)

        initial_count = len(self.exposed_wires)
        self.exposed_wires = [wire for wire in self.exposed_wires if not wire.is_off_screen(1200)]
        self.total_removed_obstacles += initial_count - len(self.exposed_wires)

        for car in self.cars:
            car.move(self.player.speed)

        self.cars = [car for car in self.cars if not car.is_off_screen()]

        self.check_collisions()

        for powerup in self.active_powerups:
            powerup.move(self.player.speed)

        player_rect = self.player.get_rect()
        for powerup in self.active_powerups[:]:
            if player_rect.intersects(powerup.get_rect()):
                self.player.apply_powerup(powerup, self)
                self.active_powerups.remove(powerup)

        self.active_powerups = [pu for pu in self.active_powerups if not pu.is_off_screen(self.height())]

        self.tile_manager.update_tiles(self.player.speed)

        self.update()

    def check_collisions(self):
        if self.player.handle_collisions(self.obstacles, self.exposed_wires):
            self.show_game_over()

    def save_record(self, distance, time):
        try:
            with open("config/leaderboard.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        if self.parent and hasattr(self.parent.main_menu, "username_label"):
            player_name = self.parent.main_menu.username_label.text()
        else:
            player_name = "UNK"
        records = data.get(str(distance), [])
        records.append({"name": player_name, "time": time})
        sorted_records = sorted(records, key=lambda x: x["time"])[:15]
        data[str(distance)] = sorted_records
        with open("config/leaderboard.json", "w") as file:
            json.dump(data, file, indent=4)

    def show_victory(self):
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        self.car_spawn_timer.stop()
        self.tower_spawn_timer.stop()
        self.car_spawn_timer.stop()
        self.exposed_wire_spawn_timer.stop()
        self.powerup_spawn_timer.stop()
        self.parent.stop_music()
        time_taken = self.elapsed_time
        self.save_record(self.target_distance, time_taken)
        msg = QMessageBox()
        msg.setWindowTitle("Победа!")
        msg.setText(f"Вы проехали {int(self.target_distance)} метров за {time_taken:.1f} сек!")
        msg.setStandardButtons(QMessageBox.Ok)
        choice = msg.exec_()
        if choice == QMessageBox.Ok:
            self.target_distance = 0
            if self.parent:
                self.parent.stop_music()
                self.parent.play_music(self.parent.menu_music_path)
                QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
                QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
                QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())

    def show_game_over(self):
        print("Игра завершена. Причина: переполнение шкалы КЗ.")
        self.is_game_over = True
        self.timer.stop()
        self.obstacle_spawn_timer.stop()
        self.car_spawn_timer.stop()
        self.tower_spawn_timer.stop()
        self.car_spawn_timer.stop()
        self.exposed_wire_spawn_timer.stop()
        self.powerup_spawn_timer.stop()
        self.parent.stop_music()

        for powerup in self.active_powerups[:]:
            if isinstance(powerup, SpeedBoost):
                powerup.deactivate(self.player, self)
            self.active_powerups.remove(powerup)

        self.toggle_green_stage(False)

        msg = QMessageBox()
        msg.setWindowTitle("Конец игры")
        msg.setText("Вы проиграли! Короткое замыкание!")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Critical)
        choice = msg.exec_()
        if choice == QMessageBox.Retry:
            self.set_target_distance(self.target_distance)
            if self.parent:
                self.parent.play_music(self.parent.game_music_path)
            self.update()
        else:
            if self.parent:
                QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
                QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
                QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())

    def toggle_pause(self):
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True

        if self.is_paused:
            self.last_frame_pixmap = self.grab()
            print("Снимок экрана успешно захвачен:", not self.last_frame_pixmap.isNull())
            self.timer.stop()
            self.obstacle_spawn_timer.stop()
            self.tower_spawn_timer.stop()
            self.car_spawn_timer.stop()
            self.exposed_wire_spawn_timer.stop()
            self.powerup_spawn_timer.stop()
            self.player.pause_short_circuit_level()
            if self.parent:
                self.parent.main_menu.current_mode = "single"
                self.parent.pause_menu.set_last_frame(self.last_frame_pixmap)
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)
            self.obstacle_spawn_timer.start(2000)
            self.tower_spawn_timer.start(8000)
            self.car_spawn_timer.start(5000)
            self.exposed_wire_spawn_timer.start(3000)
            self.powerup_spawn_timer.start(15000)
            self.time_timer.start(self.day_night.tick_interval_ms)
            self.player.resume_short_circuit_level()