from PyQt5.QtCore import Qt, QRect

class Player:
    def __init__(self, x=960, y=520, size=40):
        self.x_positions = [640, 960, 1280]
        self.current_x_index = 1
        self.x = self.x_positions[self.current_x_index]
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
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == Qt.Key_D:
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

        self.y = max(0, min(1040, self.y))

    def get_rect(self):
        return QRect(self.x, self.y, self.size, self.size)