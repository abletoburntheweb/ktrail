from PyQt5.QtCore import Qt, QRect, QTimer


class PlayerDuo:
    def __init__(self, player_id=1, y=780, size=40):
        """
        :param player_id: Идентификатор игрока (1 - справа, 2 - слева)
        :param y: Начальная Y координата
        :param size: Размер игрока (ширина и высота)
        """
        # Определяем позиции в зависимости от игрока
        if player_id == 1:  # Игрок 1 (справа)
            self.x_positions = [1100, 1200, 1300]  # Правая часть экрана
            self.controls = {
                'left': Qt.Key_Left,
                'right': Qt.Key_Right,
                'speed_up': Qt.Key_Up,
                'slow_down': Qt.Key_Down
            }
        else:  # Игрок 2 (слева)
            self.x_positions = [600, 700, 800]  # Левая часть экрана
            self.controls = {
                'left': Qt.Key_A,
                'right': Qt.Key_D,
                'speed_up': Qt.Key_W,
                'slow_down': Qt.Key_S
            }

        self.current_x_index = 1  # Центральный ряд
        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size

        # Скорость
        self.speed_levels = [10, 15, 20, 25, 30]  # Уровни скорости
        self.current_speed_index = 0
        self.speed = self.speed_levels[self.current_speed_index]
        self.can_change_speed = True  # Флаг для блокировки изменения скорости

    def move(self, key):
        """Обработка движения игрока."""
        if key == self.controls['left']:  # Движение влево
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == self.controls['right']:  # Движение вправо
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

    def change_speed(self, key):
        """Изменение скорости игрока."""
        if not self.can_change_speed:
            return

        if key == self.controls['speed_up']:  # Увеличение скорости
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == self.controls['slow_down']:  # Уменьшение скорости
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