import os

from PySide6.QtCore import QSortFilterProxyModel, QThread, Signal, Slot, Qt, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QLineEdit, QWidget

from constants.role_constants import RoleConstants
from utils.audio_metadata_utils import AudioMetaDataUtils
from utils.database_utils import DataBaseUtils




class DataManager(QWidget):
    inited_with_settings = Signal(QSortFilterProxyModel)
    change_selected_model = Signal(QSortFilterProxyModel)
    def __init__(self):
        super().__init__()
        self.model_list = []
        self.total_data_model = QStandardItemModel()
        # 设置表头标签
        self.total_data_model.setHorizontalHeaderLabels(["歌曲名", "歌手", "专辑"])
        self.total_music = QSortFilterProxyModel()
        self.total_music.setSourceModel(self.total_data_model)
        self.favor_music = FavoriteFilterProxyModel()
        self.favor_music.setSourceModel(self.total_data_model)
        self.model_list.append(self.total_music)
        self.model_list.append(self.favor_music)


    @Slot()
    def init_with_settings(self, settings):
        '''根据设置的扫描目录进行异步歌曲扫描'''
        line_edit: QLineEdit = settings.setting_scan_dir_lineedit
        scan_path = line_edit.text()
        self.scaner = MusicScanner(scan_path)
        self.scaner.add_item.connect(self.add_item)
        self.scaner.finished.connect(lambda: self.inited_with_settings.emit(self.total_music))
        self.scaner.finished.connect(self.init_custom_model)
        self.scaner.start()

    @Slot()
    def add_item(self, metadata: dict):
        '''其他线程向ItemModel中添加数据'''
        # 创建三个可见列的 Item
        item_title = QStandardItem(metadata['title'])
        item_artist = QStandardItem(metadata['artist'])
        item_album = QStandardItem(metadata['album'])

        item_is_favorate =metadata['is_favorite']
        item_full_path =metadata['full_path']
        item_id =metadata['id']

        # ⚠️ 关键：将绝对路径存储在第一列的 UserRole 中
        item_title.setData(item_full_path, RoleConstants.store_full_path_role)
        item_title.setData(item_is_favorate, RoleConstants.store_is_favorite_role)
        item_title.setData(item_id, RoleConstants.store_music_id_role)
        # 将这一行的三个 Item 添加到模型
        self.total_data_model.appendRow([item_title, item_artist, item_album])

    @Slot()
    def change_model(self,index:int):
        self.change_selected_model.emit(self.model_list[index])

    @Slot()
    def init_custom_model(self):
        conn = DataBaseUtils.get_new_connection()
        playlists :list[tuple] = DataBaseUtils.get_all_playlists(conn)
        if len(playlists) > 0:
            for playlist in playlists:
                self.create_new_model(playlist[0])
                self.update_playlist_songs(len(self.model_list)-1)



    @Slot()
    def create_new_model(self,playlist_id:int):
        playlist_model = PlaylistFilterProxyModel(playlist_id)
        playlist_model.setSourceModel(self.total_data_model)
        self.model_list.append(playlist_model)

    @Slot()
    def update_playlist_songs(self, playlist_index: int):
        """更新指定歌单包含的歌曲"""
        if 2 <= playlist_index < len(self.model_list):  # 索引2开始是自定义歌单
            proxy_model = self.model_list[playlist_index]
            if isinstance(proxy_model, PlaylistFilterProxyModel):
                self.scaner = PlaylistScanner(proxy_model.playlist_id)
                self.scaner.songs_loaded.connect(proxy_model.update_music_ids)
                self.scaner.start()



'''
异步扫描文件夹下的所有音频
'''
class MusicScanner(QThread):
    # 信号：发送单个文件的元数据
    add_item = Signal(dict)

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
                        'id':music[0],
                        'full_path':music[1],
                        'title': music[2],
                        'artist': music[3],
                        'album': music[4],
                        'is_favorite':music[7]
                    }
                    self.add_item.emit(metadata)
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

class PlaylistScanner(QThread):
    songs_loaded = Signal(set)
    def __init__(self,playlist_id):
        super().__init__()
        self.playlist_id=playlist_id

    def run(self, /) -> None:
        conn = DataBaseUtils.get_new_connection()
        try:
            music_ids = DataBaseUtils.get_playlist_music_ids(conn, self.playlist_id)
            self.songs_loaded.emit(music_ids)
        finally:
            conn.close()

class FavoriteFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        # 从源模型中获取该行的 is_favorite 数据
        index = self.sourceModel().index(source_row, 0, source_parent)
        is_favorite = self.sourceModel().data(index, RoleConstants.store_is_favorite_role)

        # 只返回 is_favorite 为 1 (或 True) 的行
        return is_favorite == 1

class PlaylistFilterProxyModel(QSortFilterProxyModel):
    def __init__(self,playlist_id:int, parent=None):
        super().__init__(parent)
        self.playlist_id = playlist_id
        self.music_ids = set()

    def update_music_ids(self, music_ids: set):
        """动态更新歌单包含的歌曲ID"""
        self.music_ids = music_ids
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        music_id = self.sourceModel().data(index, RoleConstants.store_music_id_role)
        return music_id in self.music_ids if music_id is not None else False