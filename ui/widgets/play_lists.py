from PySide6.QtCore import Signal, Slot, Qt

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QListWidget, \
    QInputDialog, QAbstractItemView, QStyledItemDelegate

from ui.widgets.settings import Settings
from utils.database_utils import DataBaseUtils

class CenterAlignDelegate(QStyledItemDelegate):
    '''实现item居中'''
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class PlayLists(QWidget):
    change_playlist = Signal(int)
    create_playlist_finished = Signal(int)
    def __init__(self,settings:Settings,parent =None):
        super().__init__(parent)
        self.setFixedHeight(350)
        self.settings_widget = settings
        self._ui_init()
        self._connect_signals_and_slots()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self._default_list_init()
        self._add_playlist_button_init()
        self._custom_list_init()
        self._buttom_spacer_init()
        self._settings_button_init()
        self._playlists_init()


    def _default_list_init(self):
        '''默认列表'''
        self.my_music = QPushButton('我的音乐')
        self.my_music.setFixedHeight(40)
        self.like = QPushButton('喜欢')
        self.like.setFixedHeight(40)

        self.main_layout.addWidget(self.my_music)
        self.main_layout.addWidget(self.like)

    def _add_playlist_button_init(self):
        '''添加播放列表的按钮'''
        self.add_playlist_button=QPushButton('新建播放列表')
        self.add_playlist_button.setFixedHeight(40)
        self.main_layout.addWidget(self.add_playlist_button)

    def _custom_list_init(self):
        '''用户创建的歌单列表'''
        self.custom_play_lists = QListWidget()
        self.delegate = CenterAlignDelegate()
        self.custom_play_lists.setItemDelegate(self.delegate)
        self.custom_play_lists.setStyleSheet('''QListWidget::item {
                                                    height: 40px;
                                                }''')



        self.custom_play_lists.setSizePolicy(self.custom_play_lists.sizePolicy().horizontalPolicy(),QSizePolicy.Policy.Preferred)
        self.custom_play_lists.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self._update_list_height()

        self.main_layout.addWidget(self.custom_play_lists)
    def _buttom_spacer_init(self):
        '''底部空白区域填充'''
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addSpacerItem(self.spacer)

    def _settings_button_init(self):
        self.settings_button=QPushButton('设置')
        self.settings_button.setFixedHeight(40)
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

    def _playlists_init(self):
        '''初始化custom_play_lists'''
        try:
            conn = DataBaseUtils.get_new_connection()
            playlists:list[tuple] = DataBaseUtils.get_all_playlists(conn)
            if len(playlists) > 0:
                for playlist in playlists:
                    self.custom_play_lists.addItem(playlist[1])
                self._update_list_height()
        finally:
            conn.close()

    @Slot()
    def init_with_changed_settings(self):
        '''用于用户更改扫描目录,清空创建的所有歌单'''
        self.custom_play_lists.clear()
        self._update_list_height()

    @Slot()
    def add_new_playlist(self):
        '''新建播放列表'''
        text, ok = QInputDialog.getText(None, "新建播放列表", "请输入歌单名称:")
        if ok and text:
            try:
                conn = DataBaseUtils.get_new_connection()
                playlist_id = DataBaseUtils.create_playlist(conn,text)
                self.create_playlist_finished.emit(playlist_id)
                self.custom_play_lists.addItem(text)
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

        self.custom_play_lists.setFixedHeight(min(height, 190))

