import os
import sys

from PySide6.QtWidgets import QApplication

from qss.qss_manager import get_style
from ui.main_window import MainWindow


app = QApplication()
window = MainWindow()
window.setStyleSheet(get_style())
window.show()
sys.exit(app.exec())