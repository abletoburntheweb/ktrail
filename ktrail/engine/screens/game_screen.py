from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

        # Параметры для тайлов
        self.tile_size = 192
        self.rows = 6  # Количество видимых рядов
        self.columns = 10  # Количество тайлов в ряду
        self.tile_colors = [
            QColor(255, 0, 0),    # Красный
            QColor(0, 0, 255),    # Синий
            QColor(0, 255, 0),    # Зеленый
            QColor(255, 255, 0),  # Желтый
            QColor(255, 0, 255),  # Фиолетовый
            QColor(0, 255, 255),  # Голубой
            QColor(128, 0, 0),    # Темно-красный
            QColor(0, 128, 0),    # Темно-зеленый
            QColor(0, 0, 128),    # Темно-синий
            QColor(128, 128, 0)   # Оливковый
        ]
        self.current_color_index = 0
        self.tile_positions = []

        self.initialize_tiles()

        # Таймер для анимации движения тайлов (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_tiles_down)
        self.timer.start(16)  # Обновление каждые ~16 мс (≈60 FPS)

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Игровой экран")
        self.setFixedSize(1920, 1080)

    def initialize_tiles(self):
        """Инициализация начальных позиций тайлов."""
        for row in range(self.rows):
            for col in range(self.columns):
                x = col * self.tile_size
                y = row * self.tile_size
                color_index = (row + col) % len(self.tile_colors)
                self.tile_positions.append((x, y, color_index))

    def move_tiles_down(self):
        """Перемещение тайлов вниз."""
        if not hasattr(self, "is_paused") or not self.is_paused:
            new_tile_positions = []
            for x, y, color_index in self.tile_positions:
                y += 2
                if y > self.height():
                    y = -self.tile_size
                    color_index = (color_index + 1) % len(self.tile_colors)
                new_tile_positions.append((x, y, color_index))
            self.tile_positions = new_tile_positions
            self.update()

    def paintEvent(self, event):
        """Отрисовка тайлов."""
        painter = QPainter(self)
        for x, y, color_index in self.tile_positions:
            color = self.tile_colors[color_index]
            painter.fillRect(x, y, self.tile_size, self.tile_size, color)

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш."""
        if event.key() == Qt.Key_Escape:
            print("Пауза...")
            self.toggle_pause()

    def toggle_pause(self):
        """Переключение состояния паузы."""
        if hasattr(self, "is_paused"):
            self.is_paused = not self.is_paused
        else:
            self.is_paused = True

        if self.is_paused:
            self.timer.stop()
            if self.parent:
                self.parent.setCurrentWidget(self.parent.pause_menu)
        else:
            self.timer.start(16)