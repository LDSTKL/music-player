import os

from PySide6.QtCore import QSortFilterProxyModel, QThread, Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QLineEdit, QWidget

from utils.audio_metadata_utils import AudioMetaDataUtils
from utils.database_utils import DataBaseUtils

store_full_path_role = Qt.ItemDataRole.UserRole
store_music_list_role = Qt.ItemDataRole.UserRole + 1

class DataManager(QWidget):
    inited_with_settings = Signal(QSortFilterProxyModel)
    def __init__(self):
        super().__init__()
        self.total_data_model = QStandardItemModel()
        # 设置表头标签
        self.total_data_model.setHorizontalHeaderLabels(["歌曲名", "歌手", "专辑"])
        self.total_music = QSortFilterProxyModel()
        self.total_music.setSourceModel(self.total_data_model)
        self.favor_music = QSortFilterProxyModel()
        self.favor_music.setSourceModel(self.total_data_model)


    @Slot()
    def init_with_settings(self, settings):
        '''根据设置的扫描目录进行异步歌曲扫描'''
        line_edit: QLineEdit = settings.setting_scan_dir_lineedit
        scan_path = line_edit.text()
        self.scaner = MusicScanner(scan_path)
        self.scaner.add_item.connect(self.add_item)
        self.scaner.finished.connect(lambda: self.inited_with_settings.emit(self.total_music))
        self.scaner.start()

    @Slot()
    def add_item(self, metadata: dict, full_path: str):
        '''向ItemModel中添加数据'''
        # 创建三个可见列的 Item
        item_title = QStandardItem(metadata['title'])
        item_artist = QStandardItem(metadata['artist'])
        item_album = QStandardItem(metadata['album'])

        # ⚠️ 关键：将绝对路径存储在第一列的 UserRole 中
        item_title.setData(full_path, store_full_path_role)
        item_title.setData(-1, store_music_list_role)
        # 将这一行的三个 Item 添加到模型
        self.total_data_model.appendRow([item_title, item_artist, item_album])


'''
异步扫描文件夹下的所有音频
'''
class MusicScanner(QThread):
    # 信号：发送单个文件的元数据
    add_item = Signal(dict, str)

    # finished = Signal()  # QThread自带finished信号

    def __init__(self, scan_path):
        super().__init__()
        self.scan_path = scan_path

    def run(self):
        # 数据库中有数据,读取数据库
        conn = DataBaseUtils.get_new_connection()
        try:
            music_list = DataBaseUtils.select_all_music(conn)

            if len(music_list) > 0:
                for music in music_list:
                    metadata = {
                        'title': music[2],
                        'artist': music[3],
                        'album': music[4]
                    }
                    full_path = music[1]
                    self.add_item.emit(metadata, full_path)
            else:
                # 数据库中没有数据,扫描文件夹
                for file in os.listdir(self.scan_path):
                    if file.endswith('.mp3'):
                        full_path = os.path.join(self.scan_path, file)
                        metadata = AudioMetaDataUtils.get_music_meta(full_path)
                        # 添加数据到data_model
                        self.add_item.emit(metadata, full_path)
                        # 更新数据库
                        DataBaseUtils.insert_or_update_music(conn, full_path, metadata['title']
                                                             , metadata['artist']
                                                             , metadata['album']
                                                             , metadata['genre']
                                                             , metadata['year'])
        finally:
            conn.close()