from PyQt5.QtCore import Qt, QRect, QTimer


class Player:
    def __init__(self, y=780, size=40):
        # Позиции по оси X
        self.x_positions = [704, 954, 1204]
        self.current_x_index = 1  # Начальная позиция (центр)
        self.x = self.x_positions[self.current_x_index]
        self.y = y
        self.size = size

        # Уровни скорости: 3 - стандартная скорость
        self.speed_levels = [10, 15, 20, 25, 30]  # Скорости
        self.current_speed_index = 2  # Начальная скорость (3-й уровень)
        self.speed = self.speed_levels[self.current_speed_index]

        self.can_change_speed = True  # Флаг для блокировки изменения скорости

        # Шкала короткого замыкания (КЗ)
        self.short_circuit_level = 0  # Текущий уровень КЗ (0 - минимальный, 100 - максимальный)
        self.short_circuit_max = 100  # Максимальное значение КЗ
        self.short_circuit_timer = QTimer()  # Таймер для обновления шкалы КЗ
        self.short_circuit_timer.timeout.connect(self.update_short_circuit)
        self.short_circuit_timer.start(100)  # Обновление каждые 100 мс

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

    def change_speed(self, key):
        """Изменение скорости игрока."""
        if not self.can_change_speed:
            return

        old_speed_index = self.current_speed_index

        if key == Qt.Key_W:  # Увеличение скорости
            if self.current_speed_index < len(self.speed_levels) - 1:
                self.current_speed_index += 1
        elif key == Qt.Key_S:  # Уменьшение скорости
            if self.current_speed_index > 0:
                self.current_speed_index -= 1

        # Обновляем текущую скорость
        self.speed = self.speed_levels[self.current_speed_index]

        # Логика изменения шкалы КЗ
        if self.current_speed_index > 2:  # Если скорость выше стандартной
            pass  # Шкала КЗ увеличивается автоматически через таймер
        elif self.current_speed_index < 2 and self.short_circuit_level > 0:  # Добавлена проверка на ноль
            decrease_rate = 0.5 if self.current_speed_index == 1 else 1.0  # На 2-й скорости медленнее, на 1-й быстрее
            self.short_circuit_level = max(0, self.short_circuit_level - decrease_rate)
        # При переходе на стандартную скорость (3-й уровень) шкала КЗ не меняется

        self.can_change_speed = False  # Блокируем изменение скорости
        QTimer.singleShot(200, self.enable_speed_change)  # Разблокируем через 200 мс

    def enable_speed_change(self):
        """
        Разблокировка изменения скорости.
        """
        self.can_change_speed = True

    def move(self, key):
        """
        Обработка движения игрока.
        :param key: Код клавиши (Qt.Key_A или Qt.Key_D).
        """
        if key == Qt.Key_A:  # Движение влево
            if self.current_x_index > 0:
                self.current_x_index -= 1
                self.x = self.x_positions[self.current_x_index]
        elif key == Qt.Key_D:  # Движение вправо
            if self.current_x_index < len(self.x_positions) - 1:
                self.current_x_index += 1
                self.x = self.x_positions[self.current_x_index]

    def get_current_speed(self):
        """
        Возвращает текущую скорость.
        """
        return self.speed

    def get_short_circuit_level(self):
        """
        Возвращает текущий уровень КЗ.
        """
        return self.short_circuit_level

    def get_rect(self):
        """
        Возвращает прямоугольник (QRect) для коллизий.
        """
        return QRect(int(self.x), int(self.y), self.size, self.size)