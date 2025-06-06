# engine/screens/obstacle.py

from random import choice
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor


class Obstacle:
    def __init__(self, screen_width, screen_height, size=40):
        self.size = size
        self.x_positions = [704, 954, 1204]  # Координаты x для препятствий
        self.x = choice(self.x_positions)  # Случайный выбор позиции
        self.y = -self.size
        self.speed = 10

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
    def __init__(self, line_width=12, color="#89878c"):
        """
        Класс для отрисовки линий, по которым движется игрок.
        :param line_width: Ширина линий.
        :param color: Цвет линий (HEX-строка).
        """
        self.x_positions = [704, 954, 1204]  # Координаты x для линий
        self.line_width = line_width
        self.color = QColor(color)  # Преобразуем HEX-строку в QColor

    def draw(self, painter, screen_height):
        """
        Отрисовка линий.
        :param painter: QPainter для отрисовки.
        :param screen_height: Высота экрана.
        """
        for x_position in self.x_positions:
            line_x = x_position + 14  # Центрируем линию относительно позиции
            painter.fillRect(line_x, 0, self.line_width, screen_height, self.color)


class TransmissionTower:
    def __init__(self, screen_height, platform_width=540, platform_height=30, gap=150):
        """
        Класс для представления опоры ЛЭП.

        :param screen_height: Высота экрана для расчета начальной позиции.
        :param platform_width: Ширина платформ (верхней и нижней).
        :param platform_height: Высота платформ.
        :param gap: Расстояние между верхней и нижней платформами.
        """
        # Начинаем с верхней границы экрана + дополнительное смещение
        self.y = -platform_height - screen_height  # Спавн выше экрана
        self.platform_width = platform_width
        self.platform_height = platform_height
        self.gap = gap
        self.screen_height = screen_height

        # Центрируем опору по горизонтали
        center_x = 960  # Центр экрана
        self.top_platform = QRect(center_x - platform_width // 2, self.y, platform_width, platform_height)
        self.bottom_platform = QRect(center_x - platform_width // 2, self.y + gap + platform_height, platform_width,
                                     platform_height)

        # Линии
        self.line_positions = [710, 960, 1210]  # Позиции линий

    def move(self, speed):
        """Перемещение опоры вниз."""
        self.y += speed
        self.top_platform.translate(0, speed)
        self.bottom_platform.translate(0, speed)

    def draw(self, painter):
        """Отрисовка опоры."""
        # Цвет платформ
        platform_color = QColor(255, 165, 0)  # Оранжевый цвет

        # Рисуем верхнюю и нижнюю платформы
        painter.fillRect(self.top_platform, platform_color)
        painter.fillRect(self.bottom_platform, platform_color)

    def is_off_screen(self):
        """Проверяет, вышла ли опора за пределы экрана."""
        return self.bottom_platform.top() > self.screen_height