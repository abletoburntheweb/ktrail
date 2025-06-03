# engine/screens/settings_menu.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SettingsMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_fullscreen = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(1920, 1080)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Заголовок
        title_label = QLabel("Настройки")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Кнопка переключения полноэкранного режима
        self.fullscreen_toggle = QCheckBox("Полноэкранный режим")
        self.fullscreen_toggle.setFont(QFont("Arial", 18))
        self.fullscreen_toggle.setChecked(self.is_fullscreen)
        self.fullscreen_toggle.stateChanged.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_toggle)

        back_button = QPushButton("Вернуться в главное меню")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.return_to_main_menu)
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

    def return_to_main_menu(self):
        """ Вернуться в главное меню """
        print("Возвращение в главное меню...")
        if self.parent:
            self.parent.setCurrentWidget(self.parent.main_menu)