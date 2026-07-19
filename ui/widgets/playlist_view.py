'''
播放列表
'''


from PySide6.QtCore import Slot, Signal, QModelIndex, QSortFilterProxyModel, Qt, QPoint, QEvent
from PySide6.QtGui import QAction, QStandardItemModel, QColor, QBrush
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableView, \
    QHeaderView, QAbstractItemView, QMenu, QStyledItemDelegate, QLabel, QVBoxLayout

from commons.enhanced_widget import HoverTableView
from constants.role_constants import RoleConstants
from ui.widgets.data_manager import FavoriteFilterProxyModel, PlaylistFilterProxyModel
from utils.database_utils import DataBaseUtils



class PlayListView(QWidget):
    '''
    歌曲列表
    '''
    play_selected = Signal(str, list)
    add_to_playlist = Signal(int,int) # 前者是音乐id,后者是歌单下标
    remove_from_playlist = Signal(int,int) # 前者是音乐id,后者是歌单id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_data_model: QSortFilterProxyModel = None
        self.curr_music_list = []
        self.add_to_playlist_actions=[]
        self._ui_init()
        self.init_add_to_playlist_actions()
        self._connect_signal_and_slot()

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self._init_table()


    def _init_table(self):
        self.table_view = HoverTableView()
        # 隐藏左侧的行号列
        self.table_view.verticalHeader().hide()
        # 让列宽自适应内容
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 1. 设置选择行为为“整行选择”
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # 2. (可选) 设置选择模式为“单选”，防止按住 Ctrl 多选
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 禁止所有编辑操作（包括双击、按键输入等）
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 开启自带的排序功能
        self.table_view.setSortingEnabled(True)
        # 禁用表头选中高亮
        self.table_view.horizontalHeader().setHighlightSections(False)
        # 设置表头高
        self.table_view.verticalHeader().setDefaultSectionSize(30)
        # 实现平滑滚动
        self.table_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # 开启上下文菜单
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 隐藏网格线（物理上移除分隔线）
        self.table_view.setShowGrid(False)
        self.main_layout.addWidget(self.table_view)

    @Slot()
    def init_add_to_playlist_actions(self):
        self.add_to_playlist_actions.clear()
        conn = DataBaseUtils.get_new_connection()
        try:
            playlists:list[tuple] = DataBaseUtils.get_all_playlists(conn)
            if len(playlists) > 0:
                for playlist in playlists:
                    self.add_to_playlist_actions.append(playlist[1])
        finally:
            conn.close()



    def _connect_signal_and_slot(self):
        self.table_view.doubleClicked.connect(self.on_double_clicked)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

    @Slot()
    def on_double_clicked(self, proxy_index: QModelIndex):
        '''双击播放音乐'''
        # 拿到源对象和源对象中对应的索引
        source_index = self.proxy_data_model.mapToSource(proxy_index)
        source_model = self.proxy_data_model.sourceModel()

        # QModelIndex包含行和列,该方法获取同行第0列
        title = source_index.siblingAtColumn(0)
        item = source_model.itemFromIndex(title)

        path = item.data(RoleConstants.store_full_path_role)  # 根据role拿到保存的数据

        self.play_selected.emit(path, self.curr_music_list)

    @Slot()
    def show_context_menu(self,pos:QPoint):
        index = self.table_view.indexAt(pos)
        source_index = self.proxy_data_model.mapToSource(index)
        source_model = self.proxy_data_model.sourceModel()
        title_index = source_index.siblingAtColumn(0)
        item = source_model.itemFromIndex(title_index)
        music_id = item.data(RoleConstants.store_music_id_role)

        context_menu = QMenu(self)
        if isinstance(self.proxy_data_model,FavoriteFilterProxyModel):
            action = context_menu.addAction('从喜欢中移除')
            action.triggered.connect(lambda :self.remove_from_playlist.emit(music_id,0)) # id=0表示“喜欢”歌单
        elif isinstance(self.proxy_data_model,PlaylistFilterProxyModel):
            action = context_menu.addAction('从当前歌单移除')
            action.triggered.connect(lambda: self.remove_from_playlist.emit(music_id,self.proxy_data_model.playlist_id))
        else:
            add_to_playlist_menu = context_menu.addMenu('添加到歌单')
            action = add_to_playlist_menu.addAction('喜欢')
            action.triggered.connect(lambda: self.add_to_playlist.emit(music_id, 1))
            for index, action_name in enumerate(self.add_to_playlist_actions):
                action = add_to_playlist_menu.addAction(action_name)
                action.triggered.connect(lambda :self.add_to_playlist.emit(music_id,index+2))

        context_menu.exec(self.table_view.viewport().mapToGlobal(pos))

    @Slot()
    def change_data_model(self, model: QSortFilterProxyModel):
        '''切换模型的时候生成curr_music_list,且只生成一次,避免重复生成提高效率'''
        self.proxy_data_model = model
        self.table_view.setModel(self.proxy_data_model)

        self.curr_music_list.clear()

        # 2. 遍历当前过滤后的模型
        for row in range(model.rowCount()):
            # 获取第 0 列（Title列）的索引
            index = model.index(row, 0)

            # 通过 UserRole 获取存储的路径
            # 注意：这里假设你存路径的 role 变量名为 store_full_path_role
            file_path = model.data(index, RoleConstants.store_full_path_role)

            if file_path:
                self.curr_music_list.append(file_path)


