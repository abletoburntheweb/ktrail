from PyQt5.QtCore import Qt, QRect, QTimer


class Player:
    def __init__(self, y=520, size=40):
        self.x_positions = [704, 954, 1204]
        self.current_x_index = 1
        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size
        self.speed_levels = [10, 15, 20, 25, 30]
        self.current_speed_index = 0
        self.speed = self.speed_levels[self.current_speed_index]
        self.can_change_speed = True  # Флаг для блокировки изменения скорости

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
        if not self.can_change_speed:
            return

        if key == Qt.Key_W:  # Увеличение скорости
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == Qt.Key_S:  # Уменьшение скорости
            if self.current_speed_index > 0:
                self.current_speed_index -= 1

        # Обновляем текущую скорость
        self.speed = self.speed_levels[self.current_speed_index]

        self.can_change_speed = False  # Блокируем изменение скорости
        QTimer.singleShot(200, self.enable_speed_change)  # Разблокируем через 200 мс

    def enable_speed_change(self):
        """Разблокировка изменения скорости."""
        self.can_change_speed = True

    def get_rect(self):
        """Возвращает прямоугольник для коллизий."""
        return QRect(int(self.x), self.y, self.size, self.size)

    def get_current_speed(self):
        """Возвращает текущую скорость."""
        return self.speed