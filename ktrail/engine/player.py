from PyQt5.QtCore import Qt, QRect

class Player:
    def __init__(self, y=520, size=40):
        self.x_positions = [704, 954, 1204]  # Фиксированные позиции полос
        self.current_x_index = 1  # Начальная полоса (центральная)
        self.x = self.x_positions[self.current_x_index]  # Текущая позиция по X
        self.y = y  # Фиксированная позиция по Y
        self.size = size  # Размер игрока
        self.speed_levels = [10, 15, 20, 25, 30]  # Доступные скорости
        self.current_speed_index = 0  # Индекс текущей скорости (по умолчанию первая)
        self.speed = self.speed_levels[self.current_speed_index]  # Текущая скорость

    def move(self, key):
        """Обработка движения игрока."""
        if key == Qt.Key_A:  # Движение влево
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == Qt.Key_D:  # Движение вправо
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

    def change_speed(self, key):
        """Изменение скорости игрока."""
        if key == Qt.Key_W:  # Увеличение скорости
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == Qt.Key_S:  # Уменьшение скорости
            if self.current_speed_index > 0:
                self.current_speed_index -= 1

        # Обновляем текущую скорость
        self.speed = self.speed_levels[self.current_speed_index]

    def get_rect(self):
        """Возвращает прямоугольник для коллизий."""
        return QRect(int(self.x), self.y, self.size, self.size)

    def get_current_speed(self):
        """Возвращает текущую скорость."""
        return self.speed