from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QRadialGradient


class PlayerDuo:
    def __init__(self, player_id=1, y=840, size=40):
        if player_id == 1:
            self.x_positions = [1313, 1567, 1807]
            self.controls = {
                'left': Qt.Key_Left,
                'right': Qt.Key_Right,
                'speed_up': Qt.Key_Up,
                'slow_down': Qt.Key_Down
            }
        else:
            self.x_positions = [73, 327, 567]
            self.controls = {
                'left': 30,
                'right': 32,
                'speed_up': 17,
                'slow_down': 31
            }
        self.player_id = player_id

        self.current_x_index = 1
        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size

        self.speed_levels = [10, 15, 20, 25, 30]
        self.current_speed_index = 2
        self.speed = self.speed_levels[self.current_speed_index]
        self.can_change_speed = True

        self.speed_change_block_timer = QTimer()
        self.speed_change_block_timer.timeout.connect(self.enable_speed_change)

        self.short_circuit_level = 0
        self.short_circuit_max = 100
        self.short_circuit_timer = QTimer()
        self.short_circuit_timer.timeout.connect(self.update_short_circuit)
        self.short_circuit_timer.start(100)

        self.paused_short_circuit_level = None

        self.is_invincible = False
        self.invincibility_timer = QTimer()
        self.invincibility_timer.timeout.connect(self.disable_invincibility)
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_visibility)
        self.is_visible = True
        self.distance_penalty = 0

        self.light_radius = 80
        self.light_color = QColor("#ff6b6b") if player_id == 1 else QColor(
            "#4aa0fc")
        self.is_light_on = True
        self.is_speed_boost_active = False

        self.original_speed_levels = None
        self.original_current_speed_index = None

    def draw_light(self, painter):
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
        if key == self.controls['left']:
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == self.controls['right']:
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

    def change_speed(self, key):
        if not self.can_change_speed:
            return

        if key == self.controls['speed_up']:
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == self.controls['slow_down']:
            if self.current_speed_index > 0:
                self.current_speed_index -= 1

        self.speed = self.speed_levels[self.current_speed_index]

        self.can_change_speed = False
        QTimer.singleShot(200, self.enable_speed_change)

    def enable_speed_change(self):
        self.can_change_speed = True

    def get_rect(self):
        return QRect(int(self.x), int(self.y), self.size, self.size)

    def get_current_speed_level(self):
        return self.current_speed_index + 1

    def get_current_speed(self):
        return self.speed

    def pause_short_circuit_level(self):
        if self.short_circuit_timer.isActive():
            self.paused_short_circuit_level = self.short_circuit_level
            self.short_circuit_timer.stop()

    def resume_short_circuit_level(self):
        if not self.short_circuit_timer.isActive() and self.paused_short_circuit_level is not None:
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

        if self.short_circuit_level >= self.short_circuit_max:
            self.distance_penalty = 20
            self.enable_invincibility(5000)

    def get_short_circuit_level(self):
        return self.short_circuit_level

    def enable_invincibility(self, duration=5000):
        self.is_invincible = True
        self.invincibility_timer.start(duration)
        self.blink_timer.start(200)

    def disable_invincibility(self):
        self.is_invincible = False
        self.invincibility_timer.stop()
        self.blink_timer.stop()
        self.is_visible = True

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def apply_collision_penalty(self, penalty=20):

        self.can_change_speed = False
        self.speed_change_block_timer.start(2000)

        if self.is_speed_boost_active:
            if self.original_speed_levels is not None and self.original_current_speed_index is not None:
                self.speed_levels = self.original_speed_levels
                self.current_speed_index = self.original_current_speed_index
                self.speed = self.speed_levels[self.current_speed_index]
            else:
                self.current_speed_index = 2
                self.speed = self.speed_levels[self.current_speed_index]

            self.is_speed_boost_active = False

            if hasattr(self.parent, "toggle_green_stage"):
                self.parent.toggle_green_stage(False, self.player_id)

            return

        if 0 <= self.current_speed_index < len(self.speed_levels):
            self.current_speed_index = 2
            self.speed = self.speed_levels[self.current_speed_index]
        else:
            self.current_speed_index = max(0, min(len(self.speed_levels) - 1, 2))
            self.speed = self.speed_levels[self.current_speed_index]