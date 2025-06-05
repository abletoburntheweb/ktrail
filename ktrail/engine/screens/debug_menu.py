from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSlider, QLineEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor


class DebugMenuScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug Menu")
        self.setFixedSize(400, 600)

        # Настройки окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        layout.addWidget(self.create_label("DEBUG: Управление временем"))

        self.phase_label = self.create_label("Фаза: ---")
        layout.addWidget(self.phase_label)

        self.tick_label = self.create_label("Тики: --- / ---")
        layout.addWidget(self.tick_label)

        # Поле ввода текущего тика
        self.current_tick_input = self.create_input("Текущий тик", layout, "Текущий тик")

        # Скорость времени
        self.speed_slider = self.create_slider(layout, "Скорость времени", 1, 300, 10)

        # Хвостик
        self.trail_slider = self.create_slider(layout, "Хвост", 1, 100, 25)
        self.trail_s_slider = self.create_slider(layout, "Условная скорость", 1, 100, 10)
        self.trail_f_slider = self.create_slider(layout, "Частота", 1, 100, 16)

        # tick_interval_ms
        self.interval_input = self.create_input("tick_interval_ms (мс)", layout)

        # ticks_per_update
        self.update_ticks_input = self.create_input("ticks_per_update", layout)

        # Ползунок времени
        self.slider = self.create_slider(layout, "Текущее время", 0, 100, 0)

        layout.addWidget(self.create_label("Нажмите ~ чтобы закрыть"))

        self.setLayout(layout)

        # Таймер для обновления данных
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_from_engine)
        self.timer.start(100)  # Каждые 100 мс

        # Подключаем сигналы
        self.slider.valueChanged.connect(self.change_time_from_slider)
        self.speed_slider.valueChanged.connect(self.change_time_speed_from_slider)
        self.trail_slider.valueChanged.connect(self.trail)
        self.trail_s_slider.valueChanged.connect(self.trail_step)
        self.trail_f_slider.valueChanged.connect(self.frick)
        self.interval_input.textEdited.connect(self.change_tick_interval_manually)
        self.update_ticks_input.textEdited.connect(self.change_ticks_per_update_manually)
        self.current_tick_input.textEdited.connect(self.change_current_tick_manually)

    # --- Вспомогательные методы ---

    def create_label(self, text):
        label = QLabel(text, self)
        label.setStyleSheet("color: white;")
        return label

    def create_input(self, placeholder, layout, label_text=None):
        if label_text:
            layout.addWidget(self.create_label(label_text))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet("background-color: #2a2a2a; color: white; border: 1px solid white;")
        layout.addWidget(line_edit)
        return line_edit

    def create_slider(self, layout, label_text, min_val, max_val, default_val):
        layout.addWidget(self.create_label(label_text))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setStyleSheet("QSlider::handle:horizontal { background-color: white; }")
        layout.addWidget(slider)
        return slider

    # --- Рисование фона ---

    def paintEvent(self, event):
        """Рисуем полупрозрачный фон"""
        painter = QPainter(self)
        background_color = QColor(30, 30, 30, 200)  # Тёмно-серый с прозрачностью
        painter.fillRect(self.rect(), background_color)

    # --- Обновление информации о времени ---

    def update_debug_info(self, day_night_system):
        phase = "День" if day_night_system.is_day() else "Ночь"
        total = day_night_system.total_ticks
        current = day_night_system.current_tick
        self.phase_label.setText(f"Фаза: {phase}")
        self.tick_label.setText(f"Тики: {current} / {total}")

        # Обновляем ползунок времени
        self.slider.blockSignals(True)
        self.slider.setMaximum(total)
        self.slider.setValue(current)
        self.slider.blockSignals(False)

        # Обновляем скорость и значения
        speed = int((day_night_system.ticks_per_update / 10) * 10)
        self.speed_slider.blockSignals(True)
        self.speed_slider.setValue(speed)
        self.speed_slider.blockSignals(False)

        self.interval_input.blockSignals(True)
        self.interval_input.setText(str(day_night_system.tick_interval_ms))
        self.interval_input.blockSignals(False)

        self.update_ticks_input.blockSignals(True)
        self.update_ticks_input.setText(str(day_night_system.ticks_per_update))
        self.update_ticks_input.blockSignals(False)

        self.current_tick_input.blockSignals(True)
        self.current_tick_input.setText(str(current))
        self.current_tick_input.blockSignals(False)

    def update_from_engine(self):
        """Обновление из GameEngine"""
        if self.isVisible() and self.parent() and hasattr(self.parent(), 'game_screen'):
            day_night = self.parent().game_screen.day_night
            self.update_debug_info(day_night)

    # --- Управление событиями ---

    def keyPressEvent(self, event):
        if event.text() == '~':
            self.hide()
            if self.parent:
                self.parent().game_screen.setFocus()

    def mousePressEvent(self, event):
        """Клик по слайдеру — обновляем время"""
        if event.button() == Qt.LeftButton:
            if self.slider.geometry().contains(event.pos()):
                value = self.slider.minimum() + (
                    (self.slider.maximum() - self.slider.minimum()) *
                    (event.x() / self.slider.width())
                )
                self.slider.setValue(int(value))
                self.change_time_from_slider()

    def change_time_from_slider(self):
        """Меняем время в game_screen через родителя"""
        if self.parent() and hasattr(self.parent(), 'game_screen'):
            day_night = self.parent().game_screen.day_night
            day_night.current_tick = self.slider.value()
            self.update_debug_info(day_night)


    def trail(self):
        if self.parent() and hasattr(self.parent(), 'game_screen'):
            trail = self.parent().game_screen
            trail.max_trail_length = self.trail_slider.value()

    def trail_step(self):
        if self.parent() and hasattr(self.parent(), 'game_screen'):
            trail = self.parent().game_screen
            trail.speed = self.trail_s_slider.value()
            print(trail.speed)

    def frick(self):
        if self.parent() and hasattr(self.parent(), 'game_screen'):
            trail = self.parent().game_screen
            f = self.trail_f_slider.value()
            trail.timer.start(f)
            print(f)

    def change_time_speed_from_slider(self):
        speed_factor = self.speed_slider.value() / 10.0  # От 0.1 до 10x
        if self.parent() and hasattr(self.parent(), 'game_screen'):
            day_night = self.parent().game_screen.day_night
            day_night.tick_interval_ms = max(1, int(50 / speed_factor))  # минимальное 1 мс
            day_night.ticks_per_update = max(1, int(10 * speed_factor))

            self.interval_input.blockSignals(True)
            self.update_ticks_input.blockSignals(True)

            self.interval_input.setText(str(day_night.tick_interval_ms))
            self.update_ticks_input.setText(str(day_night.ticks_per_update))

            self.interval_input.blockSignals(False)
            self.update_ticks_input.blockSignals(False)

    def change_tick_interval_manually(self):
        try:
            value = int(self.interval_input.text())
            if value <= 0:
                return
            if self.parent() and hasattr(self.parent(), 'game_screen'):
                day_night = self.parent().game_screen.day_night
                day_night.tick_interval_ms = value

                # Пересчитываем ticks_per_update пропорционально
                day_night.ticks_per_update = max(1, int(10 * (50 / day_night.tick_interval_ms)))

                self.speed_slider.blockSignals(True)
                self.speed_slider.setValue(int(day_night.ticks_per_update / 10 * 10))
                self.speed_slider.blockSignals(False)

                self.update_ticks_input.blockSignals(True)
                self.update_ticks_input.setText(str(day_night.ticks_per_update))
                self.update_ticks_input.blockSignals(False)
        except ValueError:
            pass

    def change_ticks_per_update_manually(self):
        try:
            value = int(self.update_ticks_input.text())
            if value <= 0:
                return
            if self.parent() and hasattr(self.parent(), 'game_screen'):
                day_night = self.parent().game_screen.day_night
                day_night.ticks_per_update = value

                day_night.tick_interval_ms = max(1, int(50 * (10 / day_night.ticks_per_update)))

                self.speed_slider.blockSignals(True)
                self.speed_slider.setValue(int(day_night.ticks_per_update / 10 * 10))
                self.speed_slider.blockSignals(False)

                self.interval_input.blockSignals(True)
                self.interval_input.setText(str(day_night.tick_interval_ms))
                self.interval_input.blockSignals(False)
        except ValueError:
            pass

    def change_current_tick_manually(self):
        try:
            value = int(self.current_tick_input.text())
            if self.parent() and hasattr(self.parent(), 'game_screen'):
                day_night = self.parent().game_screen.day_night
                day_night.current_tick = value
                self.update_debug_info(day_night)
        except ValueError:
            pass