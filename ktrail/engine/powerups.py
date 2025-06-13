from random import choice
from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtGui import QColor


class PowerUp:
    """
    Базовый класс для всех паверапов.
    """
    def __init__(self, screen_width, screen_height, size=40, duration=7000):
        """
        :param screen_width: Ширина экрана.
        :param screen_height: Высота экрана.
        :param size: Размер паверапа (ширина и высота).
        :param duration: Длительность эффекта в миллисекундах.
        """
        self.x_positions = [704, 954, 1204]  # Координаты x для паверапов
        self.size = size
        self.x = choice(self.x_positions)  # Случайный выбор позиции
        self.y = -self.size  # Начальная позиция за пределами экрана
        self.speed = 10  # Скорость движения паверапа
        self.duration = duration
        self.is_active = False  # Флаг активации паверапа
        self.timer = QTimer()  # Таймер для отслеживания длительности эффекта

    def move(self):
        """
        Перемещение паверапа вниз.
        """
        self.y += self.speed

    def activate(self, player):
        """
        Активация паверапа.
        :param player: Экземпляр игрока.
        """
        raise NotImplementedError("Метод activate должен быть реализован в дочерних классах.")

    def deactivate(self, player):
        """
        Деактивация паверапа.
        :param player: Экземпляр игрока.
        """
        raise NotImplementedError("Метод deactivate должен быть реализован в дочерних классах.")

    def get_rect(self):
        """
        Возвращает прямоугольник для проверки коллизий.
        """
        return QRect(self.x, self.y, self.size, self.size)

    def is_off_screen(self, delete_y):
        """
        Проверяет, достиг ли паверап заданной координаты y.
        :param delete_y: Координата y, на которой паверап должен быть удален.
        :return: True, если паверап достиг или пересек delete_y.
        """
        return self.y >= delete_y


class SpeedBoost(PowerUp):
    """
    Паверап, увеличивающий скорость игрока.
    """
    def __init__(self, screen_width, screen_height, size=40, duration=7000, boost_amount=30):
        super().__init__(screen_width, screen_height, size, duration)
        self.boost_amount = boost_amount
        self.original_speed_levels = None  # Для сохранения исходных уровней скорости
        self.original_current_speed_index = None  # Для сохранения текущего индекса скорости
        self.color = QColor("#00FF00")  # Зеленый цвет

    def activate(self, player):
        """
        Активация бустера скорости.
        :param player: Экземпляр игрока.
        """
        if not self.is_active:
            self.is_active = True
            # Сохраняем исходные данные о скорости
            self.original_speed_levels = player.speed_levels[:]
            self.original_current_speed_index = player.current_speed_index  # Сохраняем текущий индекс
            # Устанавливаем фиксированную скорость 30 м/с
            player.speed_levels = [30]  # Только один уровень скорости
            player.current_speed_index = 0  # Фиксируем индекс скорости
            player.speed = 30  # Обновляем текущую скорость
            player.can_change_speed = False  # Блокируем изменение скорости
            # Запускаем таймер для деактивации
            self.timer.timeout.connect(lambda: self.deactivate(player))
            self.timer.start(self.duration)

    def deactivate(self, player):
        """
        Деактивация бустера скорости.
        :param player: Экземпляр игрока.
        """
        if self.is_active:
            self.is_active = False
            # Восстанавливаем исходные уровни скорости
            player.speed_levels = self.original_speed_levels
            # Восстанавливаем исходный индекс скорости
            player.current_speed_index = self.original_current_speed_index
            # Обновляем текущую скорость на основе восстановленного индекса
            player.speed = player.speed_levels[player.current_speed_index]
            player.can_change_speed = True  # Разблокируем изменение скорости
            self.timer.stop()