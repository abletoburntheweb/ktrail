from PyQt5.QtGui import QColor, QLinearGradient

class DayNightSystem:
    def __init__(self):
        # Время
        self.day_ticks = 54000
        self.night_ticks = 54000
        self.total_ticks = self.day_ticks + self.night_ticks
        self.current_tick = 8200

        # Цвета
        self.color_day = QColor(255, 255, 255, 40)
        self.color_sunset = QColor(255, 165, 0, 100)
        self.color_night_top = QColor(0, 0, 30, 180)
        self.color_night_bottom = QColor(0, 0, 0, 180)
        self.color_dawn = QColor(255, 100, 80, 100)

        # Настройки обновления времени
        self.tick_interval_ms = 50
        self.ticks_per_update = 10

    def update_time(self):
        self.current_tick += self.ticks_per_update
        if self.current_tick > self.total_ticks:
            self.current_tick = 0

    def is_day(self):
        return self.current_tick <= self.day_ticks

    def get_current_overlay_color(self):
        progress = self.current_tick / self.total_ticks

        keyframes = [
            (0.0, self.color_night_top),
            (0.1, self.color_dawn),
            (0.5, self.color_day),
            (0.7, self.color_sunset),
            (0.95, self.color_night_top)
        ]

        current_color = self.color_night_top
        for i in range(len(keyframes) - 1):
            start_progress, start_color = keyframes[i]
            end_progress, end_color = keyframes[i + 1]

            if start_progress <= progress <= end_progress:
                t = (progress - start_progress) / (end_progress - start_progress)
                current_color = self.lerp_color(start_color, end_color, t)
                break

        return current_color

    def get_background_gradient(self, height):
        current_color = self.get_current_overlay_color()

        gradient = QLinearGradient(0, 0, 0, height)
        if current_color == self.color_night_top:
            grad_top = self.color_night_top
            grad_bottom = self.color_night_bottom
        else:
            grad_top = current_color
            grad_bottom = QColor(0, 0, 0, int(current_color.alpha() * 1.2))

        gradient.setColorAt(0, grad_top)
        gradient.setColorAt(1, grad_bottom)
        return gradient

    def should_draw_light(self):
        if not self.is_day():
            return True
        else:
            day_progress = self.current_tick / self.day_ticks
            return day_progress < 0.15 or day_progress > 0.85

    @staticmethod
    def lerp_color(c1, c2, t):
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        return QColor(r, g, b, a)