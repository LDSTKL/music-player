'''
播放列表
'''
import os
from threading import Thread

from PySide6.QtCore import Slot, QThread, Signal, QModelIndex, QSortFilterProxyModel
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
        self.proxy_data_model:QSortFilterProxyModel=None
        self._ui_init()
        self._init_table()
        self._connect_signal_and_slot()

    def _ui_init(self):
        self.main_layout = QHBoxLayout(self)

    def _init_table(self):
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
        # 开启自带的排序功能
        self.table_view.setSortingEnabled(True)
        self.main_layout.addWidget(self.table_view)

    def _connect_signal_and_slot(self):
        self.table_view.doubleClicked.connect(self.on_double_clicked)

    @Slot()
    def on_double_clicked(self,proxy_index:QModelIndex):
        # 拿到源对象和源对象中对应的索引
        source_index = self.proxy_data_model.mapToSource(proxy_index)
        source_model = self.proxy_data_model.sourceModel()

        # QModelIndex包含行和列,该方法获取同行第0列
        title = source_index.siblingAtColumn(0)
        item = source_model.itemFromIndex(title)

        path = item.data(store_full_path_role) # 根据role拿到保存的数据
        music_list = item.data(store_music_list_role) # 根据role拿到保存的数据
        self.play_selected.emit(path,music_list)

    @Slot()
    def change_data_model(self,model:QSortFilterProxyModel):
        self.proxy_data_model = model
        self.table_view.setModel(self.proxy_data_model)
