import os

from PySide6.QtCore import QSortFilterProxyModel, QThread, Signal, Slot, Qt, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QLineEdit, QWidget

from commons.enhanced_widget import HoverProxyModel
from constants.role_constants import RoleConstants
from utils.audio_metadata_utils import AudioMetaDataUtils
from utils.database_utils import DataBaseUtils




class DataManager(QWidget):
    '''歌曲数据模型管理'''
    inited_with_settings = Signal(QSortFilterProxyModel)
    change_selected_model = Signal(QSortFilterProxyModel)
    delete_playlist_finished = Signal()
    def __init__(self):
        super().__init__()
        self.scaners:list[QThread]=[]
        self.model_list = []
        self.total_data_model = QStandardItemModel()
        # 设置表头标签
        self.total_data_model.setHorizontalHeaderLabels(["歌曲名", "歌手", "专辑"])

        self.search_music = SearchFilterProxyModel()
        self.search_music.setSourceModel(self.total_data_model) # 展示搜索结果，不保存到model_list
        self.total_music = HoverProxyModel()
        self.total_music.setSourceModel(self.total_data_model)
        self.favor_music = FavoriteFilterProxyModel()
        self.favor_music.setSourceModel(self.total_data_model)
        self.model_list.append(self.total_music)
        self.model_list.append(self.favor_music)


    @Slot()
    def init_with_settings(self, scan_path:str):
        '''根据设置的扫描目录进行异步歌曲扫描,并把扫描到各歌曲信息添加到total_data_model'''
        scaner = MusicScanner(scan_path)
        scaner.add_item.connect(self.add_item_to_total_data_model)
        scaner.finished.connect(lambda: self.inited_with_settings.emit(self.total_music))
        scaner.finished.connect(self.init_custom_model)
        scaner.finished.connect(scaner.deleteLater)
        self.scaners.append(scaner)
        scaner.start()

    @Slot()
    def init_custom_model(self):
        '''total_data_model的数据初始化完成后,初始化以它为source的代理模型'''
        conn = DataBaseUtils.get_new_connection()
        playlists: list[tuple] = DataBaseUtils.get_all_playlists(conn)
        if len(playlists) > 0:
            for playlist in playlists:
                self.create_new_custom_model(playlist[0])
                self.init_custom_model_data(len(self.model_list) - 1)

    @Slot()
    def create_new_custom_model(self, playlist_id: int):
        '''创建自定义歌单数据模型'''
        playlist_model = PlaylistFilterProxyModel(playlist_id)
        playlist_model.setSourceModel(self.total_data_model)
        self.model_list.append(playlist_model)

    @Slot()
    def init_custom_model_data(self, playlist_index: int):
        """从数据库中初始化自定义歌单包含的歌曲"""
        if 2 <= playlist_index < len(self.model_list):  # 索引2开始是自定义歌单
            proxy_model = self.model_list[playlist_index]
            if isinstance(proxy_model, PlaylistFilterProxyModel):
                scaner = PlaylistScanner(proxy_model.playlist_id)
                scaner.songs_loaded.connect(proxy_model.update_music_ids)
                scaner.finished.connect(scaner.deleteLater)
                self.scaners.append(scaner)
                scaner.start()

    @Slot()
    def init_with_changed_settings(self,scan_path:str):
        conn = DataBaseUtils.get_new_connection()
        try:
            DataBaseUtils.clear_all_data(conn)
            self.total_data_model.clear()
            self.init_with_settings(scan_path)
        finally:
            conn.close()



    @Slot()
    def add_item_to_total_data_model(self, metadata: dict):
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
        '''play_lists中用户切换歌单时'''
        self.change_selected_model.emit(self.model_list[index])
    @Slot()
    def change_search_music_model(self,keyword:str):
        '''搜索功能'''
        self.search_music.set_keyword(keyword)
        self.change_selected_model.emit(self.search_music)


    @Slot()
    def add_to_a_playlist(self,music_id:int,model_index:int):
        conn = DataBaseUtils.get_new_connection()
        try:
            if model_index == 1:
                # 更新数据库中 is_favorite 的状态
                DataBaseUtils.toggle_favorite(conn,music_id,1)
                for row in range(self.total_data_model.rowCount()):
                    item = self.total_data_model.item(row, 0)
                    # 遍历找到设为is_favorite的音乐所在的item
                    if item and item.data(RoleConstants.store_music_id_role) == music_id:
                        item.setData(1, RoleConstants.store_is_favorite_role)
                        break

                    # 3. 刷新收藏过滤模型
                self.favor_music.invalidateFilter()

            elif 2 <= model_index < len(self.model_list):  # 索引2开始是自定义歌单
                proxy_model: PlaylistFilterProxyModel = self.model_list[model_index]
                DataBaseUtils.add_to_playlist(conn, proxy_model.playlist_id, music_id)
                # 刷新过滤模型
                proxy_model.update_music_ids([*proxy_model.music_ids,music_id])
        finally:
            conn.close()

    @Slot()
    def remove_from_a_playlist(self,music_id,playlist_id):
        conn = DataBaseUtils.get_new_connection()
        try:
            if playlist_id == 0:
                DataBaseUtils.toggle_favorite(conn,music_id,0)
                for row in range(self.total_data_model.rowCount()):
                    item =self.total_data_model.item(row,0)
                    if item.data(RoleConstants.store_music_id_role) ==music_id:
                        item.setData(0,RoleConstants.store_is_favorite_role)
                # 刷新模型中的数据
                self.model_list[1].invalidateFilter()
            else:
                DataBaseUtils.remove_from_playlist(conn,playlist_id,music_id)
                for model in self.model_list[2:]:
                    if model.playlist_id == playlist_id:
                        model.music_ids.remove(music_id)
                        # 刷新模型中的数据
                        model.update_music_ids(model.music_ids)
                        break
        finally:
            conn.close()
    @Slot()
    def delete_a_custom_model(self,row:int):
        if row <2:
            return
        removed_model:PlaylistFilterProxyModel = self.model_list.pop(row)
        conn = DataBaseUtils.get_new_connection()
        try:
            DataBaseUtils.delete_playlist(conn,removed_model.playlist_id)
            self.delete_playlist_finished.emit()
            self.change_selected_model.emit(self.model_list[0])
        finally:
            conn.close()



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
        '''扫描文件夹中的音乐,并且文件夹中多于数据库中的音乐被视为新增的音乐,少于数据库中的音乐被视为删除的音乐'''
        conn = DataBaseUtils.get_new_connection()
        try:
            music_list = DataBaseUtils.select_all_music(conn)
            music_paths = {music[1] for music in music_list}
            folder_music_paths = set()
            for file in os.listdir(self.scan_path):
                if file.endswith('.mp3'):
                    folder_music_paths.add(os.path.join(self.scan_path, file))

            # 计算差集
            new_files = folder_music_paths - music_paths  # 新增的音乐
            deleted_files = music_paths - folder_music_paths #删除的音乐

            # 4. 处理新增文件
            for full_path in new_files:
                metadata = AudioMetaDataUtils.get_music_meta(full_path)

                music_id = DataBaseUtils.insert_or_update_music(conn, full_path, metadata['title']
                                                                , metadata['artist']
                                                                , metadata['album']
                                                                , metadata['genre']
                                                                , metadata['year']
                                                                )
                metadata = {**metadata, 'id': music_id, 'full_path': full_path, 'is_favorite': 0}
                self.add_item.emit(metadata)

            # 5. 处理删除文件：从数据库删除
            for full_path in deleted_files:
                DataBaseUtils.delete_music_by_path(conn, full_path)

            # 6. 重新发送数据库中未变化的文件（用于UI初始化）
            for music in music_list:
                if music[1] not in new_files and music[1] not in deleted_files:
                    metadata = {
                        'id': music[0],
                        'full_path': music[1],
                        'title': music[2],
                        'artist': music[3],
                        'album': music[4],
                        'is_favorite': music[7]
                    }
                    self.add_item.emit(metadata)
        finally:
            conn.close()

class PlaylistScanner(QThread):
    songs_loaded = Signal(set) # 该歌单中歌曲id的集合
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

class FavoriteFilterProxyModel(HoverProxyModel):
    '''默认歌单：喜欢'''
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        # 从源模型中获取该行的 is_favorite 数据
        index = self.sourceModel().index(source_row, 0, source_parent)
        is_favorite = self.sourceModel().data(index, RoleConstants.store_is_favorite_role)

        # 只返回 is_favorite 为 1 (或 True) 的行
        return is_favorite == 1

class PlaylistFilterProxyModel(HoverProxyModel):
    '''用户自定义歌单'''
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


class SearchFilterProxyModel(HoverProxyModel):
    '''搜索结果'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword = ""

    def set_keyword(self, keyword: str):
        """设置搜索关键词并刷新过滤"""
        self.keyword = keyword.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if not self.keyword:
            return True

        # 检查歌曲名、歌手、专辑是否包含关键词
        for col in range(3):  # 标题、歌手、专辑三列
            index = self.sourceModel().index(source_row, col, source_parent)
            text = self.sourceModel().data(index, Qt.DisplayRole)
            if text and self.keyword in text.lower():
                return True

        return False