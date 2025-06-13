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
        self.current_speed_index = 2
        self.speed = self.speed_levels[self.current_speed_index]
        self.can_change_speed = True  # Флаг для блокировки изменения скорости

        # Шкала короткого замыкания (КЗ)
        self.short_circuit_level = 0  # Текущий уровень КЗ (0 - минимальный, 100 - максимальный)
        self.short_circuit_max = 100  # Максимальное значение КЗ
        self.short_circuit_timer = QTimer()  # Таймер для обновления шкалы КЗ
        self.short_circuit_timer.timeout.connect(self.update_short_circuit)
        self.short_circuit_timer.start(100)  # Обновление каждые 100 мс

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

        # Используем клавиши из словаря self.controls
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
        return QRect(int(self.x), int(self.y), self.size, self.size)

    def get_current_speed(self):
        """Возвращает текущую скорость."""
        return self.speed

    def update_short_circuit(self):
        """
        Обновление шкалы КЗ в зависимости от текущей скорости.
        """
        if self.short_circuit_level <= 0 and self.current_speed_index < 2:
            # Если уровень КЗ уже ноль и скорость ниже стандартной,
            # то просто выходим из метода без изменений
            return

        if self.current_speed_index > 2:  # Если скорость выше стандартной
            increase_rate = 0.5 if self.current_speed_index == 3 else 1.0
            self.short_circuit_level = min(self.short_circuit_max, self.short_circuit_level + increase_rate)
        elif self.current_speed_index < 2:  # Если скорость ниже стандартной
            decrease_rate = 0.5 if self.current_speed_index == 1 else 1.0
            self.short_circuit_level = max(0, self.short_circuit_level - decrease_rate)

        # Защита от выхода за границы
        self.short_circuit_level = max(0, min(self.short_circuit_max, self.short_circuit_level))

    def get_short_circuit_level(self):
        """
        Возвращает текущий уровень КЗ.
        """
        return self.short_circuit_level
