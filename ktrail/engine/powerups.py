from random import choice
from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtGui import QColor, QPixmap


class PowerUp:

    def __init__(self, screen_width, screen_height, size=100, duration=7000):

        self.x_positions = [662, 916, 1162]
        self.size = size
        self.x = choice(self.x_positions)
        self.y = -self.size
        self.speed = 10
        self.duration = duration
        self.is_active = False
        self.timer = QTimer()

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
        self.original_speed_levels = None
        self.original_current_speed_index = None
        self.color = QColor("#00FF00")

    def activate(self, player, game_screen):
        if not self.is_active:
            self.is_active = True
            self.original_speed_levels = player.speed_levels[:]
            self.original_current_speed_index = player.current_speed_index
            player.speed_levels = [30]
            player.current_speed_index = 0
            player.speed = 30
            player.can_change_speed = False
            if hasattr(game_screen, "toggle_green_stage"):
                game_screen.toggle_green_stage(True)
            self.timer.timeout.connect(lambda: self.deactivate(player, game_screen))
            self.timer.start(self.duration)


    def deactivate(self, player, game_screen):
        if self.is_active:
            self.is_active = False
            player.speed_levels = self.original_speed_levels
            player.current_speed_index = self.original_current_speed_index
            player.speed = player.speed_levels[player.current_speed_index]
            player.can_change_speed = True
            if hasattr(game_screen, "toggle_green_stage"):
                game_screen.toggle_green_stage(False)
            self.timer.stop()