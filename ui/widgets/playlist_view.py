'''
播放列表
'''
import os
from threading import Thread

from PySide6.QtCore import Slot, QThread, Signal, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QTableView, \
    QHeaderView, QSizePolicy, QAbstractItemView

from utils.audio_metadata_utils import AudioMetaDataUtils
from utils.database_utils import DataBaseUtils

store_full_path_role = Qt.ItemDataRole.UserRole
store_music_list_role = Qt.ItemDataRole.UserRole + 1

class PlayListView(QWidget):
    play_selected= Signal(str,int)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._ui_init()
        self._init_table()
        self._connect_signal_and_slot()

    def _ui_init(self):
        self.main_layout = QHBoxLayout(self)

    def _init_table(self):
        self.data_model = QStandardItemModel()
        # 设置表头标签
        self.data_model.setHorizontalHeaderLabels(["歌曲名", "歌手", "专辑"])
        self.table_view = QTableView()

        # 可选：隐藏左侧的行号列
        # self.table_view.verticalHeader().hide()
        # 可选：让列宽自适应内容
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 1. 设置选择行为为“整行选择”
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # 2. (可选) 设置选择模式为“单选”，防止按住 Ctrl 多选
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 禁止所有编辑操作（包括双击、按键输入等）
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.main_layout.addWidget(self.table_view)

    def _connect_signal_and_slot(self):
        self.table_view.doubleClicked.connect(self.on_double_clicked)

    @Slot()
    def on_double_clicked(self,index:QModelIndex):
        # QModelIndex包含行和列,该方法获取同行第0列
        title = index.siblingAtColumn(0)
        item = self.data_model.itemFromIndex(title)
        path = item.data(store_full_path_role) # 根据role拿到保存的数据
        music_list = item.data(store_music_list_role) # 根据role拿到保存的数据
        self.play_selected.emit(path,music_list)


    @Slot()
    def init_with_settings(self,settings):
        '''根据设置的扫描目录进行异步歌曲扫描'''
        line_edit:QLineEdit = settings.setting_scan_dir_lineedit
        scan_path = line_edit.text()
        self.scaner = MusicScanner(scan_path)
        self.scaner.add_item.connect(self.add_item)
        self.scaner.finished.connect(lambda :self.table_view.setModel(self.data_model))
        self.scaner.start()

    @Slot()
    def add_item(self,metadata:dict,full_path:str):
        # 创建三个可见列的 Item
        item_title = QStandardItem(metadata['title'])
        item_artist = QStandardItem(metadata['artist'])
        item_album = QStandardItem(metadata['album'])

        # ⚠️ 关键：将绝对路径存储在第一列的 UserRole 中
        item_title.setData(full_path, store_full_path_role)
        item_title.setData(-1, store_music_list_role)
        # 将这一行的三个 Item 添加到模型
        self.data_model.appendRow([item_title, item_artist, item_album])





'''
异步扫描文件夹下的所有音频
'''
class MusicScanner(QThread):
    # 信号：发送单个文件的元数据
    add_item = Signal(dict,str)
    # finished = Signal()  # QThread自带finished信号

    def __init__(self, scan_path):
        super().__init__()
        self.scan_path = scan_path

    def run(self):
        # 数据库中有数据,读取数据库
        conn = DataBaseUtils.get_new_connection()
        try:
            music_list = DataBaseUtils.select_all_music(conn)

            if len(music_list)>0:
                for music in music_list:
                    metadata={
                        'title':music[2],
                        'artist':music[3],
                        'album':music[4]
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
                        self.add_item.emit(metadata,full_path)
                        # 更新数据库
                        DataBaseUtils.insert_or_update_music(conn,full_path,metadata['title']
                                                             ,metadata['artist']
                                                             ,metadata['album']
                                                             ,metadata['genre']
                                                             ,metadata['year'])
        finally:
            conn.close()











