# car.py

from PyQt5.QtCore import QRect
from random import choice


class Car:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Размеры машины
        self.width = 384
        self.height = 768

        # Правый ряд (аналогично препятствиям)
        self.x = 192  # Фиксированная позиция — правый ряд
        self.y = screen_height + self.height  # Начинаем ниже экрана

        # Скорость движения вверх
        self.speed = 10

        # Загрузка текстуры
        from PyQt5.QtGui import QPixmap
        self.texture = QPixmap("assets/textures/dev_car.png").scaled(self.width, self.height)

    def move(self):
        """Движение вверх"""
        self.y -= self.speed

    def is_off_screen(self):
        """Проверяет, ушла ли машина за верх экрана"""
        return self.y + self.height < 0

    def get_rect(self):
        """Возвращает QRect для проверки столкновений (если понадобится)"""
        return QRect(self.x, self.y, self.width, self.height)