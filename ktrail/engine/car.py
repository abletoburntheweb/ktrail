from PyQt5.QtCore import QRect
from random import randint
from PyQt5.QtGui import QPixmap


class Car:
    TEXTURE_PATHS = [f"assets/textures/car/car{i}.png" for i in range(1, 15)]

    last_car_rect = None  # Прямоугольник последней созданной машины

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.width = 384
        self.height = 768

        # Генерируем случайные координаты
        self.x = randint(-60, 380)
        self.y = screen_height + self.height

        # Проверяем коллизию с последней машиной
        if Car.last_car_rect:
            new_rect = QRect(self.x, self.y, self.width, self.height)
            if new_rect.intersects(Car.last_car_rect):
                self.x = -500

        # Сохраняем свой прямоугольник как последний
        Car.last_car_rect = QRect(self.x, self.y, self.width, self.height)

        self.speed = 10

        # Загрузка текстуры
        texture_path = Car.TEXTURE_PATHS[randint(0, len(Car.TEXTURE_PATHS) - 1)]
        self.texture = QPixmap(texture_path).scaled(self.width, self.height)

    def draw(self, painter):
        if self.texture and not self.is_off_screen():
            painter.drawPixmap(self.x, self.y, self.texture)

    def move(self, speed):
        self.y -= self.speed - speed // 4

    def is_off_screen(self):
        return self.y + self.height < 0

    def get_rect(self):
        return QRect(self.x, self.y, self.width, self.height)