# engine/screens/distance_selection.py

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from engine.rotating_panel import RotatingPanel


class DistanceSelection(QWidget):
    SOLO_DISTANCES = [25000, 30000, 45000, 58000]
    DUO_DISTANCES = [20000, 30000, 35000, 38000]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_duo = False
        self.widgets_to_animate = []
        self.distance_buttons = []
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(1920, 1080)

        self.distance_buttons = []

        self.distance_buttons = []
        for _ in range(4):
            button = QPushButton("", self)
            button.setFixedSize(120, 120)
            button.hide()
            self.widgets_to_animate.append(button)
            self.distance_buttons.append(button)

        self.back_button = QPushButton("Назад", self)
        self.back_button.setFont(QFont("Arial", 18))
        self.back_button.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: rgba(255, 255, 255, 20);
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 70)
        }
        """)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.hide()
        self.widgets_to_animate.append(self.back_button)

    def update_distance_buttons(self):
        distances = self.DUO_DISTANCES if self.is_duo else self.SOLO_DISTANCES
        bg_color = "#FC9E2F" if self.is_duo else "#82C8FF"

        for i, distance in enumerate(distances):
            self.distance_buttons[i].setText("")
            self.distance_buttons[i].setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border-radius: 60px;
                    border: none;
                }}
                QPushButton:hover {{
                    border: 4px solid cyan;
                }}
            """)
            try:
                self.distance_buttons[i].clicked.disconnect()
            except TypeError:
                pass
            self.distance_buttons[i].clicked.connect(lambda _, d=distance: self.start_game(d))

    def showEvent(self, event):
        super().showEvent(event)

        for widget in self.widgets_to_animate:
            widget.hide()

        self.update_distance_buttons()
        self.position_buttons()

        background_path = "assets/textures/cus2.png" if self.is_duo else "assets/textures/cus.png"

        RotatingPanel.assemble_transition(
            self,
            on_finished=self.on_animation_finished,
            background_path=background_path
        )

    def position_buttons(self):
        if self.is_duo:
            positions = [(416, 568), (800, 568), (1184, 568), (1568, 568)]
        else:
            positions = [(611, 390), (996, 390), (1381, 390), (1766, 390)]

        for i, pos in enumerate(positions):
            self.distance_buttons[i].move(*pos)
            self.distance_buttons[i].show()
            self.distance_buttons[i].raise_()

    def on_animation_finished(self):
        self.temp_background = QLabel(self)
        background_path = "assets/textures/cus2.png" if self.is_duo else "assets/textures/cus.png"
        dev_g_pixmap = QPixmap(background_path)
        scaled = dev_g_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.temp_background.setPixmap(scaled)
        self.temp_background.resize(self.size())
        self.temp_background.move(0, 0)
        self.temp_background.show()
        self.temp_background.raise_()

        for widget in self.widgets_to_animate:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            widget.anim = anim
            anim.start()
            widget.show()

            widget.raise_()
            self.enable_buttons()

    def disable_buttons(self):
        for widget in self.widgets_to_animate:
            if isinstance(widget, QPushButton):
                widget.setDisabled(True)

    def enable_buttons(self):
        for widget in self.widgets_to_animate:
            if isinstance(widget, QPushButton):
                widget.setDisabled(False)

    def start_game(self, distance):
        if self.parent:
            if not self.is_duo:
                self.parent.game_screen.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen)
            else:
                self.parent.game_screen_duo.reset_game()
                self.parent.game_screen_duo.set_target_distance(distance)
                self.parent.setCurrentWidget(self.parent.game_screen_duo)
            self.is_duo = False

    def go_back(self):
        if self.parent:
            self.parent.play_cancel_sound()
            self.disable_buttons()
            QTimer.singleShot(800, lambda: RotatingPanel.start_transition(self))
            QTimer.singleShot(2700, lambda: self.parent.setCurrentWidget(self.parent.main_menu))
            QTimer.singleShot(2700, lambda: self.parent.main_menu.restore_positions())