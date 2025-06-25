from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QRadialGradient, QBrush

class Player:
    def __init__(self, y=780, size=40):
        self.x_positions = [695, 948, 1190]
        self.current_x_index = 1
        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size

        self.speed_levels = [10, 15, 20, 25, 30]
        self.current_speed_index = 2
        self.speed = self.speed_levels[self.current_speed_index]

        self.can_change_speed = True

        self.short_circuit_level = 0
        self.paused_short_circuit_level = None
        self.short_circuit_max = 100
        self.short_circuit_timer = QTimer()
        self.short_circuit_timer.timeout.connect(self.update_short_circuit)
        self.short_circuit_timer.start(100)

        # Свет игрока
        self.light_radius = 80
        self.light_color = QColor("#4aa0fc")
        self.is_light_on = True

        # Трейл
        self.trail = []
        self.max_trail_length = 20
        self.trail_width = 10
        self.trail_start_color = QColor("#4aa0fc")
        self.trail_end_color = QColor("#FFFFFF")
        self.target_trail_x = self.x + 15
        self.current_trail_x = self.target_trail_x
        self.trail_transition_speed = 5

    def draw_player_light(self, painter):
        if self.is_light_on:
            light_pos_x = self.x + self.size // 2
            light_pos_y = self.y + self.size // 2
            gradient = QRadialGradient(light_pos_x, light_pos_y, self.light_radius)
            gradient.setColorAt(0, self.light_color)
            gradient.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos_x - self.light_radius,
                                light_pos_y - self.light_radius,
                                self.light_radius * 2,
                                self.light_radius * 2)


    def move(self, key):
        if key == Qt.Key_A:
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
                self.target_trail_x = self.x + 15
        elif key == Qt.Key_D:
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]
                self.target_trail_x = self.x + 15

    def change_speed(self, key):
        if not self.can_change_speed:
            return

        old_speed_index = self.current_speed_index

        if key == Qt.Key_W:
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == Qt.Key_S:
            if self.current_speed_index > 0:
                self.current_speed_index -= 1

        self.speed = self.speed_levels[self.current_speed_index]

        if self.current_speed_index > 2:
            pass
        elif self.current_speed_index < 2 and self.short_circuit_level > 0:
            decrease_rate = 0.5 if self.current_speed_index == 1 else 1.0
            self.short_circuit_level = max(0, self.short_circuit_level - decrease_rate)

        self.can_change_speed = False
        QTimer.singleShot(200, self.enable_speed_change)

    def enable_speed_change(self):
        self.can_change_speed = True

    def pause_short_circuit_level(self):
        self.paused_short_circuit_level = self.short_circuit_level
        self.short_circuit_timer.stop()

    def resume_short_circuit_level(self):
        if self.paused_short_circuit_level is not None:
            self.short_circuit_level = self.paused_short_circuit_level
            self.paused_short_circuit_level = None
            self.short_circuit_timer.start(100)

    def update_short_circuit(self):
        if self.short_circuit_level <= 0 and self.current_speed_index < 2:
            return

        if self.current_speed_index > 2:
            increase_rate = 0.5 if self.current_speed_index == 3 else 1.0
            self.short_circuit_level = min(self.short_circuit_max, self.short_circuit_level + increase_rate)
        elif self.current_speed_index < 2:
            decrease_rate = 0.5 if self.current_speed_index == 1 else 1.0
            self.short_circuit_level = max(0, self.short_circuit_level - decrease_rate)

        self.short_circuit_level = max(0, min(self.short_circuit_max, self.short_circuit_level))

    def get_current_speed(self):
        return self.speed

    def get_current_speed_level(self):
        return self.current_speed_index + 1

    def get_short_circuit_level(self):
        return self.short_circuit_level

    def get_rect(self):
        return QRect(int(self.x), int(self.y), self.size, self.size)

    def update_trail(self, speed):
        if self.current_trail_x != self.target_trail_x:
            delta = self.target_trail_x - self.current_trail_x
            step = delta / self.trail_transition_speed
            self.current_trail_x += step

        num_points = 1
        for i in range(num_points):
            factor = i / num_points
            interpolated_x = int(self.current_trail_x + (self.target_trail_x - self.current_trail_x) * factor)
            y_offset = i * (speed // num_points)
            self.trail.insert(0, (interpolated_x, self.y - y_offset))

        if len(self.trail) > self.max_trail_length:
            self.trail = self.trail[:self.max_trail_length]

        self.trail = [(x, y + speed) for x, y in self.trail]

    def draw_trail(self, painter):
        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (1 - (i / self.max_trail_length) ** 2))
            factor = i / self.max_trail_length
            r, g, b = self.trail_start_color.red(), self.trail_start_color.green(), self.trail_start_color.blue()
            r2, g2, b2 = self.trail_end_color.red(), self.trail_end_color.green(), self.trail_end_color.blue()
            ir = r + (r2 - r) * factor
            ig = g + (g2 - g) * factor
            ib = b + (b2 - b) * factor
            color = QColor(int(ir), int(ig), int(ib), alpha)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(x, y, self.trail_width, self.trail_width)

    def check_collision_with(self, obj):
        return self.get_rect().intersects(obj.get_rect())

    def handle_collisions(self, obstacles, exposed_wires):
        for obstacle in obstacles:
            if self.check_collision_with(obstacle):
                return True
        for wire in exposed_wires:
            if self.check_collision_with(wire):
                return True
        return False

    def apply_powerup(self, powerup, game_screen=None):
        if hasattr(powerup, "activate"):
            powerup.activate(self, game_screen)

    def remove_powerup(self, powerup, game_screen=None):
        if hasattr(powerup, "deactivate"):
            powerup.deactivate(self, game_screen)