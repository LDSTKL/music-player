'''
播放列表
'''
import os

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QHBoxLayout, QLabel


class MusicItem(QWidget):
    def __init__(self,music_name,artist_name,album_name):
        super().__init__()
        self.music_name = music_name
        self.artist_name =artist_name
        self.album_name = album_name

    def _ui_init(self):
        self.main_layout = QHBoxLayout(self)
        self.music_name_label = QLabel(self.music_name)
        self.artist_name_label = QLabel(self.artist_name)
        self.album_name_label = QLabel(self.album_name)
        self.main_layout.addWidget(self.music_name_label)
        self.main_layout.addWidget(self.artist_name_label)
        self.main_layout.addWidget(self.album_name_label)

class PlayListView(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.music_list=[]
        self.music_list_view = QListWidget()

    @Slot()
    def init_with_settings(self,settings):
        print('init_with_settings')
        line_edit:QLineEdit = settings.setting_scan_dir_lineedit
        scan_path = line_edit.text()
        for file in os.listdir(scan_path):
            if file.endswith('.mp3'):
                self.music_list.append(os.path.join(scan_path,file))
                self.music_list_view.addItem(QListWidgetItem())









