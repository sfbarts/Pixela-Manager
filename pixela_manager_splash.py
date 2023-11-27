from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6 import uic

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Pixela-Splash-Qt_v001.ui", self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)


