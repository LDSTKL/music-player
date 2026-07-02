import os
import sys

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def load_qss_files():
    qss_files = os.listdir('./qss')
    qss_content = ""
    for file_path in qss_files:
        with open('qss/'+file_path, 'r', encoding='utf-8') as f:
            qss_content += f.read() + "\n"
    return qss_content

# 使用

combined_qss = load_qss_files()

app = QApplication()
window = MainWindow()

app.setStyleSheet(combined_qss)
window.show()
sys.exit(app.exec())