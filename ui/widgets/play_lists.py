from PySide6.QtCore import Signal, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QListView, QVBoxLayout


class PlayLists(QWidget):
    change_playlist = Signal(QModelIndex)
    def __init__(self,parent =None):
        super().__init__(parent)
        self._ui_init()
        self._data_model_init()
        self._list_view_init()
        self._connect_signals_and_slots()

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)


    def _data_model_init(self):
        self.data_model = QStandardItemModel()
        self.default_list = QStandardItem('我的音乐')
        self.favorate_list = QStandardItem('喜欢')
        self.data_model.appendRow(self.default_list)
        self.data_model.appendRow(self.favorate_list)

    def _list_view_init(self):
        self.play_lists = QListView()
        self.play_lists.setModel(self.data_model)
        self.main_layout.addWidget(self.play_lists)

    def _connect_signals_and_slots(self):
        self.play_lists.clicked.connect(lambda index:self.change_playlist.emit(index))
