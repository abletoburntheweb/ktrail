from random import choice
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor


class Obstacle:
    def __init__(self, screen_width, screen_height, size=40):
        self.size = size
        self.x_positions = [640, 960, 1280]  # Координаты x для препятствий
        self.x = choice(self.x_positions)  # Случайный выбор позиции
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


class PowerLine:
    def __init__(self, line_width=10, color=QColor(0, 255, 255)):
        """
        Класс для отрисовки линий, по которым движется игрок.
        :param line_width: Ширина линий.
        :param color: Цвет линий.
        """
        self.x_positions = [640, 960, 1280]  # Координаты x для линий
        self.line_width = line_width
        self.color = color

    def draw(self, painter, screen_height):
        """
        Отрисовка линий.
        :param painter: QPainter для отрисовки.
        :param screen_height: Высота экрана.
        """
        for x_position in self.x_positions:
            line_x = x_position - (self.line_width // 2)  # Центрируем линию относительно позиции
            painter.fillRect(line_x, 0, self.line_width, screen_height, self.color)
