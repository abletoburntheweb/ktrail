from PyQt5.QtGui import QPainter, QTransform
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtProperty


class RotatingPanel(QLabel):
    def __init__(self, parent=None, pixmap=None, x=0, y=0, width=100, height=100):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setGeometry(x, y, width, height)
        self._angle = 0

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        self._angle = angle
        self.update()

    angle = pyqtProperty(float, get_angle, set_angle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
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

    def start_animation(self):
        # Анимация поворота
        self.anim_angle = QPropertyAnimation(self, b"angle")
        self.anim_angle.setDuration(800)
        self.anim_angle.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_angle.setStartValue(0)
        self.anim_angle.setEndValue(180)  # Один оборот

        # Группировка
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_angle)
        self.anim_group.start()

    def assemble_animation(self):
        # Анимация поворота
        self.anim_angle = QPropertyAnimation(self, b"angle")
        self.anim_angle.setDuration(800)
        self.anim_angle.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_angle.setStartValue(-180)
        self.anim_angle.setEndValue(0)  # Один оборот

        # Группировка
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_angle)
        self.anim_group.start()
