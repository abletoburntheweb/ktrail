# engine/obstacle_duo.py
from random import choice
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QRadialGradient


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

class PowerLineDuo:
    def __init__(self, line_width=12, color="#89878c"):
        """
        Класс для отрисовки линий для обоих игроков.
        :param line_width: Ширина линий.
        :param color: Цвет линий (HEX-строка).
        """
        # Положения для всех 6 полос (3 слева, 3 справа)
        self.x_positions = [600, 700, 800, 1100, 1200, 1300]
        self.line_width = line_width
        self.color = QColor(color)

    def draw(self, painter, screen_height):
        """
        Отрисовка линий на экране.
        :param painter: QPainter для отрисовки.
        :param screen_height: Высота экрана.
        """
        for x_position in self.x_positions:
            line_x = x_position + 14  # Центрируем линию относительно позиции
            painter.fillRect(line_x, 0, self.line_width, screen_height, self.color)

class TransmissionTowerDuo:
    def __init__(self, screen_height, platform_width=540, platform_height=30, gap=150, central=True):
        """
        Класс для представления опоры ЛЭП.
        :param screen_height: Высота экрана для расчета начальной позиции.
        :param platform_width: Ширина платформ (верхней и нижней).
        :param platform_height: Высота платформ.
        :param gap: Расстояние между верхней и нижней платформами.
        :param central: Флаг, указывающий, должна ли опора спавниться на центральной линии.
        """
        self.y = -platform_height - screen_height  # Спавн выше экрана
        self.platform_width = platform_width
        self.platform_height = platform_height
        self.gap = gap
        self.screen_height = screen_height

        # Определяем центральную линию для каждого игрока
        if central:
            self.x_positions = [1100, 1200, 1300]  # Правая сторона для player1
        else:
            self.x_positions = [960, 1210]  # Левая и правая линия для player1

        self.x = choice(self.x_positions)

        # Платформы
        center_x = self.x + 14  # Центрируем опору относительно позиции
        self.top_platform = QRect(center_x - platform_width // 2, self.y, platform_width, platform_height)
        self.bottom_platform = QRect(center_x - platform_width // 2, self.y + gap + platform_height, platform_width,
                                     platform_height)

    def move(self, speed):
        """Перемещение опоры вниз."""
        self.y += speed
        self.top_platform.translate(0, speed)
        self.bottom_platform.translate(0, speed)

    def draw(self, painter):
        """Отрисовка опоры."""
        platform_color = QColor(255, 165, 0)  # Оранжевый цвет
        painter.fillRect(self.top_platform, platform_color)
        painter.fillRect(self.bottom_platform, platform_color)

    def is_off_screen(self):
        """Проверяет, вышла ли опора за пределы экрана."""
        return self.bottom_platform.top() > self.screen_height

class ExposedWireDuo:
    def __init__(self, screen_width, screen_height, min_height=200, max_height=1000):
        """
        Класс для представления вертикального оголенного провода.
        :param screen_width: Ширина экрана.
        :param screen_height: Высота экрана.
        :param min_height: Минимальная высота провода.
        :param max_height: Максимальная высота провода.
        """
        # Положения для всех 6 полос (3 слева, 3 справа)
        self.x_positions = [600, 700, 800, 1100, 1200, 1300]
        self.line_width = 12
        self.color = QColor("#f80000")  # Красный цвет

        # Выбираем случайную линию
        self.line_index = choice(range(len(self.x_positions)))
        self.x = self.x_positions[self.line_index]

        # Случайная высота провода
        self.height = choice(range(min_height, max_height + 1))

        # Начальная позиция y (выше экрана)
        self.y = -self.height

        # Скорость движения
        self.speed = 10

    def move(self):
        """Перемещение провода вниз."""
        self.y += self.speed

    def get_rect(self):
        """Возвращает QRect для проверки столкновений."""
        return QRect(self.x, self.y, self.line_width, self.height)

    def is_off_screen(self, delete_y):
        """
        Проверяет, достиг ли провод заданной координаты y.
        :param delete_y: Координата y, на которой провод должен быть удален.
        :return: True, если провод достиг или пересек delete_y.
        """
        return self.y >= delete_y

class StreetLampDuo:
    def __init__(self, screen_width, screen_height, lamp_width=40, lamp_height=80):
        """
        Класс для представления дорожного фонаря.
        :param screen_width: Ширина экрана.
        :param screen_height: Высота экрана.
        :param lamp_width: Ширина фонаря.
        :param lamp_height: Высота фонаря.
        """
        # Положения для всех 6 полос (3 слева, 3 справа)
        self.x_positions = [600, 700, 800, 1100, 1200, 1300]

        self.lamp_width = lamp_width
        self.lamp_height = lamp_height

        # Выбираем случайную линию
        self.line_index = choice(range(len(self.x_positions)))
        self.x = self.x_positions[self.line_index]

        # Начальная позиция y (выше экрана)
        self.y = -self.lamp_height

        # Скорость движения
        self.speed = 10

        # Свет фонаря
        self.light_radius = 150
        self.light_color = QColor(255, 240, 200, 120)  # Цвет света
        self.is_light_on = False  # Флаг для управления светом

    def move(self):
        """Перемещение фонаря вниз."""
        self.y += self.speed

    def get_rect(self):
        """Возвращает QRect для проверки столкновений."""
        return QRect(self.x, self.y, self.lamp_width, self.lamp_height)

    def is_off_screen(self, delete_y):
        """
        Проверяет, достиг ли фонарь заданной координаты y.
        :param delete_y: Координата y, на которой фонарь должен быть удален.
        :return: True, если фонарь достиг или пересек delete_y.
        """
        return self.y >= delete_y

    def update_light_state(self, day_night_system):
        """
        Обновляет состояние света фонаря на основе времени суток.
        :param day_night_system: Экземпляр DayNightSystem.
        """
        self.is_light_on = not day_night_system.is_day()

    def draw_light(self, painter, screen_height):
        """
        Отрисовка света фонаря.
        :param painter: QPainter для отрисовки.
        :param screen_height: Высота экрана.
        """
        if self.is_light_on:
            light_pos_x = self.x + self.lamp_width // 2
            light_pos_y = self.y + self.lamp_height
            gradient = QRadialGradient(light_pos_x, light_pos_y, self.light_radius)
            gradient.setColorAt(0, self.light_color)
            gradient.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos_x - self.light_radius,
                                light_pos_y - self.light_radius,
                                self.light_radius * 2,
                                self.light_radius * 2)