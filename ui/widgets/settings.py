import sys

from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFileDialog, QVBoxLayout, QPushButton, QLineEdit, \
    QApplication


class Settings(QWidget):
    scan_dir_changed = Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._ui_init()

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self) # 布局
        self._settings_init()

    def _settings_init(self):
        self.setting_scan_dir_layout = QHBoxLayout()
        self.setting_scan_dir_label = QLabel('扫描目录')
        self.setting_scan_dir_lineedit = QLineEdit(readOnly=True,text=r'D:\音乐')
        self.setting_scan_dir_button = QPushButton('切换目录')
        self.setting_scan_dir_button.clicked.connect(self.update_scan_dir)

        self.setting_scan_dir_layout.addWidget(self.setting_scan_dir_label)
        self.setting_scan_dir_layout.addWidget(self.setting_scan_dir_lineedit)
        self.setting_scan_dir_layout.addWidget(self.setting_scan_dir_button)

        self.main_layout.addLayout(self.setting_scan_dir_layout)


    @Slot()
    def update_scan_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Open Directory",
                                             "/home",
                                             QFileDialog.ShowDirsOnly
                                             | QFileDialog.DontResolveSymlinks)
        if path ==None or path=='':
            return
        else:
            self.setting_scan_dir_lineedit.setText(path)
            self.scan_dir_changed.emit(self.setting_scan_dir_lineedit.text())



if __name__ == '__main__':
    app = QApplication()
    window = Settings()
    window.show()
    sys.exit(app.exec())