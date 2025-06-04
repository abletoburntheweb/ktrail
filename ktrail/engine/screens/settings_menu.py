# engine/screens/settings_menu.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SettingsMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_fullscreen = False
        self.previous_screen = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Настройки")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.fullscreen_toggle = QCheckBox("Полноэкранный режим")
        self.fullscreen_toggle.setFont(QFont("Arial", 18))
        self.fullscreen_toggle.setChecked(self.is_fullscreen)
        self.fullscreen_toggle.stateChanged.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_toggle)

        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.return_to_previous_screen)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def toggle_fullscreen(self, state):
        if state == Qt.Checked:
            print("Переключение в полноэкранный режим...")
            self.parent.showFullScreen()
            self.is_fullscreen = True
        else:
            print("Переключение в оконный режим...")
            self.parent.showNormal()
            self.is_fullscreen = False

    def set_previous_screen(self, screen_name):
        """Устанавливает предыдущий экран."""
        self.previous_screen = screen_name

    def return_to_previous_screen(self):
        """Возвращает пользователя на предыдущий экран."""
        if self.previous_screen == "pause_menu":
            print("Возвращение в меню паузы...")
            if self.parent and hasattr(self.parent.game_screen, "toggle_pause"):
                self.parent.setCurrentWidget(self.parent.pause_menu)
        elif self.previous_screen == "main_menu":
            print("Возвращение в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)
        else:
            print("Неизвестный предыдущий экран. Возвращаемся в главное меню...")
            if self.parent:
                self.parent.setCurrentWidget(self.parent.main_menu)