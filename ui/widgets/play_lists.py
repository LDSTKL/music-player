from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QListView, QVBoxLayout


class PlayLists(QWidget):
    def __init__(self,parent =None):
        super().__init__(parent)
        self.play_lists = QListView()
        self.data_model = QStandardItemModel()
        self._ui_init()

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.play_lists)
        self.default_list= QStandardItem('我的音乐')
        self.favorate_list= QStandardItem('喜欢')
        self.data_model.appendRow(self.default_list)
        self.data_model.appendRow(self.favorate_list)
        self.play_lists.setModel(self.data_model)

