from PyQt5.QtCore import Qt, QRect

class PlayerDuo:
    def __init__(self, player_id=1, y=520, size=40):
        """
        :param player_id: Идентификатор игрока (1 - справа, 2 - слева)
        :param y: Начальная Y координата
        :param size: Размер игрока (ширина и высота)
        """
        # Определяем позиции в зависимости от игрока
        if player_id == 1:  # Игрок 1 (справа)
            self.x_positions = [1100, 1200, 1300]  # Правая часть экрана
            self.controls = {
                'up': Qt.Key_W,
                'down': Qt.Key_S,
                'left': Qt.Key_A,
                'right': Qt.Key_D
            }
            self.current_x_index = 1  # Центральный ряд
        else:  # Игрок 2 (слева)
            self.x_positions = [600, 700, 800]  # Левая часть экрана
            self.controls = {
                'up': Qt.Key_Up,
                'down': Qt.Key_Down,
                'left': Qt.Key_Left,
                'right': Qt.Key_Right
            }
            self.current_x_index = 1  # Центральный ряд

        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size
        self.speed = 10

    def move(self, key_pressed):
        """Обработка движения в зависимости от нажатой клавиши"""
        if key_pressed == self.controls['up']:
            self.y -= self.speed
        elif key_pressed == self.controls['down']:
            self.y += self.speed
        elif key_pressed == self.controls['left']:
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key_pressed == self.controls['right']:
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

        # Ограничение по вертикали
        self.y = max(0, min(1040, self.y))

    def get_rect(self):
        return QRect(self.x, self.y, self.size, self.size)