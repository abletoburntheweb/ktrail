from random import choice
from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtGui import QColor, QPixmap


class PowerUp:

    def __init__(self, screen_width, screen_height, size=100, duration=7000):

        self.x_positions = [662, 916, 1162]  # Координаты x для паверапов
        self.size = size
        self.x = choice(self.x_positions)  # Случайный выбор позиции
        self.y = -self.size  # Начальная позиция за пределами экрана
        self.speed = 10  # Скорость движения паверапа
        self.duration = duration
        self.is_active = False  # Флаг активации паверапа
        self.timer = QTimer()  # Таймер для отслеживания длительности эффекта

        self.texture = QPixmap("assets/textures/bat.png")

    def draw(self, painter):
        if not self.texture.isNull():
            painter.drawPixmap(self.x, self.y, 100, 100, self.texture)

    def move(self, speed):
        self.y += speed

    def activate(self, player):
        raise NotImplementedError("Метод activate должен быть реализован в дочерних классах.")

    def deactivate(self, player):
        raise NotImplementedError("Метод deactivate должен быть реализован в дочерних классах.")

    def get_rect(self):
        return QRect(self.x, self.y, 100, 100)

    def is_off_screen(self, delete_y):
        return self.y >= delete_y


class SpeedBoost(PowerUp):
    def __init__(self, screen_width, screen_height, size=40, duration=7000, boost_amount=30):
        super().__init__(screen_width, screen_height, size, duration)
        self.boost_amount = boost_amount
        self.original_speed_levels = None  # Для сохранения исходных уровней скорости
        self.original_current_speed_index = None  # Для сохранения текущего индекса скорости
        self.color = QColor("#00FF00")  # Зеленый цвет

    def activate(self, player, game_screen):
        if not self.is_active:
            self.is_active = True
            # Сохраняем исходные данные о скорости
            self.original_speed_levels = player.speed_levels[:]
            self.original_current_speed_index = player.current_speed_index
            # Устанавливаем фиксированную скорость 30 м/с
            player.speed_levels = [30]
            player.current_speed_index = 0
            player.speed = 30
            player.can_change_speed = False
            # Показываем green_stage
            if hasattr(game_screen, "toggle_green_stage"):
                game_screen.toggle_green_stage(True)
            # Запускаем таймер для деактивации
            self.timer.timeout.connect(lambda: self.deactivate(player, game_screen))
            self.timer.start(self.duration)


    def deactivate(self, player, game_screen):
        if self.is_active:
            self.is_active = False
            # Восстанавливаем исходные уровни скорости
            player.speed_levels = self.original_speed_levels
            # Восстанавливаем исходный индекс скорости
            player.current_speed_index = self.original_current_speed_index
            # Обновляем текущую скорость на основе восстановленного индекса
            player.speed = player.speed_levels[player.current_speed_index]
            player.can_change_speed = True  # Разблокируем изменение скорости
            # Скрываем green_stage
            if hasattr(game_screen, "toggle_green_stage"):
                game_screen.toggle_green_stage(False)
            # Останавливаем таймер
            self.timer.stop()