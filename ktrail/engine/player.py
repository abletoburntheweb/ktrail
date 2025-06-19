from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QRadialGradient


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
        self.short_circuit_max = 100
        self.short_circuit_timer = QTimer()
        self.short_circuit_timer.timeout.connect(self.update_short_circuit)
        self.short_circuit_timer.start(100)

        self.light_radius = 80
        self.light_color = QColor("#ff6b6b")
        self.is_light_on = True

    def draw_player_light(self, painter):
        if self.is_light_on:
            light_radius = 80
            light_color = QColor("#4aa0fc")

            player_rect = self.get_rect()
            light_pos_x = player_rect.center().x()
            light_pos_y = player_rect.center().y()

            gradient = QRadialGradient(light_pos_x, light_pos_y, light_radius)
            gradient.setColorAt(0, light_color)
            gradient.setColorAt(1, QColor(255, 240, 200, 0))

            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                light_pos_x - light_radius,
                light_pos_y - light_radius,
                light_radius * 2,
                light_radius * 2
            )

    def move(self, key):
        if key == Qt.Key_A:
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == Qt.Key_D:
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

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