# engine/screens/player.py

from PyQt5.QtCore import Qt, QRect

class Player:
    def __init__(self, x=940, y=520, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 5

    def move(self, key):
        """Обработка движения игрока."""
        if key == Qt.Key_W:
            self.y -= self.speed
        elif key == Qt.Key_S:
            self.y += self.speed
        elif key == Qt.Key_A:
            self.x -= self.speed
        elif key == Qt.Key_D:
            self.x += self.speed

        self.x = max(0, min(1880, self.x))
        self.y = max(0, min(1040, self.y))

    def get_rect(self):
        return QRect(self.x, self.y, self.size, self.size)