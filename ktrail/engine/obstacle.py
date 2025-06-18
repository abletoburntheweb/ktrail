# engine/screens/obstacle.py

from random import choice
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPixmap

class Obstacle:
    def __init__(self, screen_width, screen_height, size=40):
        self.size = size
        self.x_positions = [695, 948, 1190]
        self.x = choice(self.x_positions)
        self.y = -self.size
        self.speed = 10

        self.texture = QPixmap("assets/textures/damage.png")
    def move(self, speed):
        self.y += speed

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.x+14, self.y, 12, self.size, self.texture)

    def get_rect(self):
        return QRect(self.x+14, self.y, 12, self.size)

    def is_off_screen(self, delete_y):
        return self.y >= delete_y

class PowerLine:
    def __init__(self, line_width=12):

        self.x_positions = [695, 948, 1190]
        self.line_width = line_width

        self.texture = QPixmap("assets/textures/cabel.png")

    def draw(self, painter, screen_height):
        if self.texture.isNull():
            return
        scaled_texture = self.texture.scaled(self.line_width, screen_height)
        for x_position in self.x_positions:
            line_x = x_position + 14
            painter.drawPixmap(line_x, 0, scaled_texture.width(), scaled_texture.height(), scaled_texture)

class TransmissionTower:
    def __init__(self, screen_height, platform_width=600, platform_height=195):
        self.y = -platform_height - screen_height
        self.platform_width = platform_width
        self.platform_height = platform_height
        self.screen_height = screen_height
        center_x = 960
        self.platform = QRect(center_x - platform_width // 2, self.y, platform_width, platform_height)

        self.texture = QPixmap("assets/textures/lap.png")

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.platform, self.texture)
        else:
            painter.fillRect(self.platform, QColor(255, 165, 0))

    def move(self, speed):
        self.y += speed
        self.platform.translate(0, speed)

    def is_off_screen(self, delete_y):
        return self.y >= delete_y


class ExposedWire:
    def __init__(self, screen_width, screen_height, min_height=200, max_height=1000):
        self.x_positions = [709, 962, 1204]
        self.line_width = 12
        self.line_index = choice(range(len(self.x_positions)))
        self.x = self.x_positions[self.line_index]
        self.height = choice(range(min_height, max_height + 1))
        self.y = -self.height
        self.speed = 10

        self.texture = QPixmap("assets/textures/damage_m.png")

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.x, self.y, self.line_width, self.height, self.texture)

    def move(self, speed):
        self.y += speed

    def get_rect(self):
        return QRect(self.x, self.y, self.line_width, self.height)

    def is_off_screen(self, delete_y):
        return self.y >= delete_y
