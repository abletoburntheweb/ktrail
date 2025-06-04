# engine/obstacle.py

from PyQt5.QtCore import QRect
from random import choice


class Obstacle:
    def __init__(self, screen_width, screen_height, size=40):
        self.size = size
        self.x_positions = [640, 960, 1280]
        self.x = choice(self.x_positions)
        self.y = -self.size
        self.speed = 5

    def move(self):
        """Перемещение препятствия вниз."""
        self.y += self.speed

    def get_rect(self):
        """Возвращает QRect для проверки столкновений."""
        return QRect(self.x, self.y, self.size, self.size)

    def is_off_screen(self, delete_y):
        """
        Проверяет, достиг ли препятствие заданной координаты y.
        :param delete_y: Координата y, на которой препятствие должно быть удалено.
        :return: True, если препятствие достигло или пересекло delete_y.
        """
        return self.y >= delete_y