# engine/obstacle_duo.py
from random import choice
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor


class ObstacleDuo:
    def __init__(self, screen_width=1920, screen_height=1080, size=40):
        """
        Препятствие для дуо режима — может появляться на любой из 6 полос (3 слева, 3 справа)
        :param screen_width: Ширина экрана
        :param screen_height: Высота экрана
        :param size: Размер препятствия
        """
        # Положения для всех 6 полос (3 для каждого игрока)
        self.x_positions = [600, 700, 800, 1100, 1200, 1300]  # Левый: 600-800 | Правый: 1100-1300
        self.x = choice(self.x_positions)  # Случайная позиция
        self.y = -size  # Начинаем выше экрана
        self.size = size
        self.speed = 10  # Скорость движения вниз

    def move(self):
        """Движение препятствия вниз"""
        self.y += self.speed

    def get_rect(self):
        """Возвращает QRect для коллизий"""
        return QRect(self.x, self.y, self.size, self.size)

    def is_off_screen(self):
        """
        Проверяет, вышло ли препятствие за нижнюю границу экрана
        """
        return self.y >= 1080  # 1080 — высота экрана

    def check_collision_with_players(self, player1_rect, player2_rect):
        """
        Проверяет столкновение с обоими игроками
        :param player1_rect: QRect игрока 1
        :param player2_rect: QRect игрока 2
        :return: "player1", "player2" или None
        """
        if player1_rect.intersects(self.get_rect()):
            return "player1"
        if player2_rect.intersects(self.get_rect()):
            return "player2"
        return None