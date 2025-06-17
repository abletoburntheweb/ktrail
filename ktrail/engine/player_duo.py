from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QRadialGradient


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

        self.is_invincible = False  # Флаг неуязвимости
        self.invincibility_timer = QTimer()  # Таймер для отслеживания времени неуязвимости
        self.invincibility_timer.timeout.connect(self.disable_invincibility)
        self.blink_timer = QTimer()  # Таймер для мигания
        self.blink_timer.timeout.connect(self.toggle_visibility)
        self.is_visible = True  # Флаг видимости для мигания
        self.distance_penalty = 0  # Штраф за столкновение (в метрах)

        self.light_radius = 120  # Радиус светового эффекта
        self.light_color = QColor("#ff6b6b") if player_id == 1 else QColor("#4aa0fc")  # Цвет света для player1 и player2 соответственно
        self.is_light_on = True  # Флаг для управления светом

    def draw_light(self, painter):
        """
        Отрисовка света вокруг игрока.
        :param painter: QPainter для отрисовки.
        """
        if self.is_light_on:
            light_pos_x = self.x + self.size // 2
            light_pos_y = self.y + self.size // 2
            gradient = QRadialGradient(light_pos_x, light_pos_y, self.light_radius)
            gradient.setColorAt(0, self.light_color)
            gradient.setColorAt(1, QColor(255, 240, 200, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(light_pos_x - self.light_radius,
                                light_pos_y - self.light_radius,
                                self.light_radius * 2,
                                self.light_radius * 2)

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

        # Если уровень КЗ достиг максимума, активируем штраф
        if self.short_circuit_level >= self.short_circuit_max:
            self.distance_penalty = 20  # Устанавливаем штраф
            self.enable_invincibility(5000)  # Включаем неуязвимость на 5 секунд

    def get_short_circuit_level(self):
        """
        Возвращает текущий уровень КЗ.
        """
        return self.short_circuit_level

    def enable_invincibility(self, duration=5000):
        """Включает неуязвимость на указанное время (в миллисекундах)."""
        self.is_invincible = True
        self.invincibility_timer.start(duration)
        self.blink_timer.start(200)  # Мигание каждые 200 мс

    def disable_invincibility(self):
        """Отключает неуязвимость."""
        self.is_invincible = False
        self.invincibility_timer.stop()
        self.blink_timer.stop()
        self.is_visible = True  # Восстанавливаем видимость

    def toggle_visibility(self):
        """Переключает видимость игрока для эффекта мигания."""
        self.is_visible = not self.is_visible

    def apply_collision_penalty(self, penalty=20):
        """Применяет штраф за столкновение."""
        self.distance_penalty += penalty
        self.current_speed_index = 2  # Сбрасываем скорость до стандартной (3-й уровень)
        self.speed = self.speed_levels[self.current_speed_index]
