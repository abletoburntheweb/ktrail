# rotating_panel.py

from PyQt5.QtGui import QPainter, QTransform, QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtCore import pyqtProperty


class RotatingPanel(QLabel):
    def __init__(self, parent=None, pixmap=None, x=0, y=0, width=100, height=100):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setGeometry(x, y, width, height)
        self._angle = 0
        self.animation = None

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        self._angle = angle
        self.update()

    angle = pyqtProperty(float, get_angle, set_angle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Центр панели
        cx, cy = self.width() / 2, self.height() / 2

        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(self._angle, Qt.YAxis)
        transform.translate(-cx, -cy)

        painter.setTransform(transform)

        normalized_angle = self._angle % 360
        is_back_side = 90 < normalized_angle < 270

        if not is_back_side:
            painter.drawPixmap(0, 0, self.pixmap())
        else:
            painter.fillRect(self.rect(), Qt.black)

    def start_animation(self, delay=0):
        """Запуск анимации переворота с задержкой"""
        QTimer.singleShot(delay, self._run_animation)

    def _run_animation(self):
        if self.animation:
            self.animation.stop()
            self.animation.deleteLater()

        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setStartValue(0)
        self.animation.setEndValue(180)

        self.animation.finished.connect(lambda: QTimer.singleShot(1200, self.deleteLater))
        self.animation.start()

    def start_assemble_animation(self, delay=0):
        QTimer.singleShot(delay, self._run_assemble_animation)

    def _run_assemble_animation(self):
        if self.animation:
            self.animation.stop()
            self.animation.deleteLater()

        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setStartValue(180)
        self.animation.setEndValue(360)

        self.animation.finished.connect(lambda: QTimer.singleShot(1200, self.deleteLater))
        self.animation.start()

    @staticmethod
    def start_transition(widget, cols=10, rows=6):
        screen = widget.grab()
        tile_w = widget.width() // cols
        tile_h = widget.height() // rows

        background_pixmap = QPixmap("assets/textures/logo.png")
        background_label = QLabel(widget)
        background_label.setPixmap(
            background_pixmap.scaled(widget.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        )
        background_label.resize(widget.size())
        background_label.move(0, 0)
        background_label.show()

        panels = []

        for row in range(rows):
            for col in range(cols):
                x = col * tile_w
                y = row * tile_h
                tile_pixmap = screen.copy(x, y, tile_w, tile_h)

                panel = RotatingPanel(
                    parent=widget,
                    pixmap=tile_pixmap,
                    x=x,
                    y=y,
                    width=tile_w,
                    height=tile_h
                )
                panel.show()
                panels.append(panel)

                delay = (row + col) * 40
                panel.start_animation(delay=delay)

        QTimer.singleShot(1200, lambda: background_label.deleteLater())

    @staticmethod
    def assemble_transition(widget, on_finished=None, cols=10, rows=6, background_path="assets/textures/demo.png"):
        tile_w = widget.width() // cols
        tile_h = widget.height() // rows

        background_pixmap = QPixmap("assets/textures/logo.png")
        background_label = QLabel(widget)
        background_label.setPixmap(
            background_pixmap.scaled(widget.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        )
        background_label.resize(widget.size())
        background_label.move(0, 0)
        background_label.show()

        background_pixmap = QPixmap(background_path)
        if background_pixmap.isNull():
            print(f"Ошибка: не удалось загрузить файл '{background_path}'")
            return

        scaled_background = background_pixmap.scaled(
            widget.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        panels = []

        for row in range(rows):
            for col in range(cols):
                x = col * tile_w
                y = row * tile_h
                tile_pixmap = scaled_background.copy(x, y, tile_w, tile_h)

                panel = RotatingPanel(
                    parent=widget,
                    pixmap=tile_pixmap,
                    x=x,
                    y=y,
                    width=tile_w,
                    height=tile_h
                )
                panel.angle = 180  # Начинаем с чёрной стороны
                panel.show()
                panels.append(panel)

                delay = (rows - row + cols - col) * 40  # Волна от дальнего угла
                panel.start_assemble_animation(delay=delay)

        QTimer.singleShot(1200, lambda: background_label.deleteLater())
        if on_finished:
            QTimer.singleShot(1200, on_finished)
