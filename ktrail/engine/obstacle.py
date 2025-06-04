# engine/obstacle.py

from PyQt5.QtCore import QRect
from random import choice

class Obstacle:
    def __init__(self, screen_width, screen_height, size=40):
        self.size = size
        self.x_positions = [640, 960, 1280]  # Три фиксированные позиции по X
        self.x = choice(self.x_positions)  # Выбираем случайную позицию из фиксированных
        self.y = -self.size  # Начинаем за пределами экрана
        self.speed = 5  # Скорость движения вниз

    def move(self):
        """Перемещение препятствия вниз."""
        self.y += self.speed

    def get_rect(self):
        """Возвращает QRect для проверки столкновений."""
        return QRect(self.x, self.y, self.size, self.size)

    def is_off_screen(self, screen_height):
        """Проверяет, вышло ли препятствие за пределы экрана."""
        return self.y > screen_height