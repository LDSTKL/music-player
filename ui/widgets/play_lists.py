from PySide6.QtCore import Signal, Slot

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QListWidget, \
    QInputDialog

from ui.widgets.settings import Settings
from utils.database_utils import DataBaseUtils


class PlayLists(QWidget):
    change_playlist = Signal(int)
    create_playlist_finished = Signal(int)
    def __init__(self,settings:Settings,parent =None):
        super().__init__(parent)
        self.settings_widget = settings
        self._ui_init()
        self._connect_signals_and_slots()

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self._default_list_init()
        self._add_playlist_button_init()
        self._custom_list_init()
        self._buttom_spacer_init()
        self._settings_button_init()

    @Slot()
    def init_with_changed_settings(self):
        self.custom_play_lists.clear()
        self._update_list_height()

    def _default_list_init(self):
        '''默认列表'''
        self.my_music = QPushButton('我的音乐')
        self.like = QPushButton('喜欢')

        self.main_layout.addWidget(self.my_music)
        self.main_layout.addWidget(self.like)

    def _add_playlist_button_init(self):
        '''添加播放列表的按钮'''
        self.add_playlist_button=QPushButton('新建播放列表')
        self.main_layout.addWidget(self.add_playlist_button)

    def _custom_list_init(self):
        '''用户创建的歌单列表'''
        self.custom_play_lists = QListWidget()

        self.custom_play_lists.setSizePolicy(self.custom_play_lists.sizePolicy().horizontalPolicy(),QSizePolicy.Policy.Preferred)

        self._update_list_height()

        self.main_layout.addWidget(self.custom_play_lists)
    def _buttom_spacer_init(self):
        '''底部空白区域填充'''
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addSpacerItem(self.spacer)

    def _settings_button_init(self):
        self.settings_button=QPushButton('设置')
        self.main_layout.addWidget(self.settings_button)


    def _connect_signals_and_slots(self):
        #按钮点击
        self.my_music.clicked.connect(lambda index:self.change_playlist.emit(0))
        self.like.clicked.connect(lambda index:self.change_playlist.emit(1))
        #列表item点击
        self.custom_play_lists.clicked.connect(lambda index:self.change_playlist.emit(index.row()+2))
        #添加歌单按钮点击
        self.add_playlist_button.clicked.connect(self.add_new_playlist)
        #设置按钮点击
        self.settings_button.clicked.connect(self.settings_widget.show)

    @Slot()
    def add_new_playlist(self):
        text, ok = QInputDialog.getText(self, "新建播放列表", "请输入歌单名称:")
        if ok and text:
            try:
                conn = DataBaseUtils.get_new_connection()
                playlist_id = DataBaseUtils.create_playlist(conn,text)
                self.create_playlist_finished.emit(playlist_id)
                self.custom_play_lists.addItem(text)
                self._update_list_height()
            finally:
                conn.close()

    @Slot()
    def init_with_settings(self):
        try:
            conn = DataBaseUtils.get_new_connection()
            playlists:list[tuple] = DataBaseUtils.get_all_playlists(conn)
            if len(playlists) > 0:
                for playlist in playlists:
                    self.custom_play_lists.addItem(playlist[1])
                self._update_list_height()
        finally:
            conn.close()





    def _update_list_height(self):
        """根据 item 数量动态计算并设置列表高度"""
        count = self.custom_play_lists.count()
        if count == 0:
            height = 0
        else:
            # 获取单个 item 的高度（包含间距）
            rect = self.custom_play_lists.visualItemRect(self.custom_play_lists.item(0))
            item_height = rect.height()
            # 考虑列表边框和间距
            height = item_height * count + 4  # 4px 为安全边距

        self.custom_play_lists.setFixedHeight(min(height, 300))

