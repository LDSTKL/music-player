'''
播放列表
'''
import os
from threading import Thread

from PySide6.QtCore import Slot, QThread, Signal
from PySide6.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QHBoxLayout, QLabel

from utils.audio_metadata_utils import AudioMetaDataUtils



class PlayListView(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.music_list_view = QListWidget(self)

    @Slot()
    def init_with_settings(self,settings):
        '''根据设置的扫描目录进行歌曲扫描'''
        line_edit:QLineEdit = settings.setting_scan_dir_lineedit
        scan_path = line_edit.text()
        self.scaner = MusicScanner(scan_path)
        self.scaner.add_item.connect(self.add_item)
        self.scaner.finished.connect(self.scan_finished)
        self.scaner.start()

    @Slot()
    def add_item(self,metadata:dict):
        self.music_list_view.addItem(metadata['title'])

    @Slot()
    def scan_finished(self):
        pass
        





class MusicScanner(QThread):
    # 信号：发送单个文件的元数据
    add_item = Signal(dict)
    finished = Signal()

    def __init__(self, scan_path):
        super().__init__()
        self.scan_path = scan_path

    def run(self):
        for file in os.listdir(self.scan_path):
            if file.endswith('.mp3'):
                full_path = os.path.join(self.scan_path, file)
                metadata = AudioMetaDataUtils.get_music_meta(full_path)
                self.add_item.emit(metadata)

        self.finished.emit()











