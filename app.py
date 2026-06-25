import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.database_utils import DataBaseUtils


app = QApplication()
window = MainWindow()
window.show()
app.exec()