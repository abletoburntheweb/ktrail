from random import choice
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsItem


class ObstacleDuo:
    def __init__(self, screen_width=1920, screen_height=1080, size=40):
        self.x_positions = [600, 700, 800, 1100, 1200, 1300]
        self.x = choice(self.x_positions)
        self.y = -size
        self.size = size
        self.speed = 10

        self.texture = QPixmap("assets/textures/damage.png")

    def move(self, speed):
        self.y += speed

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.x + 14, self.y, 12, self.size, self.texture)

    def get_rect(self):
        return QRect(self.x, self.y, self.size, self.size)

    def is_off_screen(self):
        return self.y >= 1080


class PowerLineDuo:
    def __init__(self, line_width=12):
        self.line_width = line_width

        self.x_positions = [73, 327, 567, 1313, 1567, 1807]
        self.texture = QPixmap("assets/textures/cabel.png")

    def draw(self, painter, screen_height):
        if not self.texture.isNull():
            scaled_texture = self.texture.scaled(self.line_width, screen_height)
            for x_position in self.x_positions:
                line_x = x_position + 14
                painter.drawPixmap(line_x, 0, scaled_texture.width(), scaled_texture.height(), scaled_texture)


class Seporator:
    def __init__(self, line_width=520):
        self.line_width = line_width

        self.x = 700
        self.texture = QPixmap("assets/textures/sepo.png")

    def draw(self, painter, screen_height):
        if not self.texture.isNull():
            scaled_texture = self.texture.scaled(self.line_width, screen_height)
            line_x = self.x
            painter.drawPixmap(line_x, 0, scaled_texture.width(), scaled_texture.height(), scaled_texture)


class TransmissionTowerDuo:
    def __init__(self, screen_height):
        self.platform_width = 600
        self.platform_height = 195
        self.screen_height = screen_height
        self.speed = 10
        self.x = 1300

        self.y = -self.platform_height - screen_height

        self.texture = QPixmap("assets/textures/lap.png")

    def move(self, speed):
        self.y += speed

    def draw(self, painter):
        if not self.texture.isNull():
            self.platform = QRect(self.x, self.y, self.platform_width, self.platform_height)
            painter.drawPixmap(self.platform, self.texture)

    def is_off_screen(self):
        return self.y >= self.screen_height


class ExposedWireDuo:
    def __init__(self, screen_width, screen_height, min_height=200, max_height=1000):
        self.x_positions = [612, 712, 812, 1112, 1212, 1312]
        self.line_width = 12
        self.line_index = choice(range(len(self.x_positions)))
        self.x = self.x_positions[self.line_index]
        self.height = choice(range(min_height, max_height + 1))
        self.y = -self.height
        self.speed = 10

        self.texture = QPixmap("assets/textures/damage_m.png")

    def move(self, speed):
        self.y += speed

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.x + 14, self.y, self.line_width, self.height, self.texture)

    def get_rect(self):
        return QRect(self.x + 14, self.y, self.line_width, self.height)

    def is_off_screen(self, delete_y):
        return self.y >= delete_y
