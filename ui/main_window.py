
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from ui.widgets.data_manager import DataManager
from ui.widgets.play_lists import PlayLists
from ui.widgets.player_controls import PlayerControls
from ui.widgets.playlist_view import PlayListView
from ui.widgets.settings import Settings
from ui.widgets.song_info_panel import SongInfoPanel
from ui.widgets.titlebar import TitleBar
from utils.database_utils import DataBaseUtils


class MainWindow(QWidget):
    settings_inited = Signal(Settings)

    def __init__(self):
        super().__init__()
        self._database_init() # 数据库初始化
        self._data_manager_init()
        self._window_init() # 窗体初始化
        self._ui_init() # 窗体内UI初始化

    def _database_init(self):
        DataBaseUtils.init_database()

    def _data_manager_init(self):
        self.data_manager = DataManager()

    def _window_init(self):
        '''初始化窗体'''
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.resize(800, 500)

    def _ui_init(self):
        '''初始化UI'''
        self.main_layout = QVBoxLayout(self)  # 主要布局,垂直布局
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.up_part_init()
        self.left_part_init()
        self.right_part_init()

        self._song_info_panel_and_playercontrols_init()

        self._settings_init()
        self._connect_signal_and_slot()

        # 发送设置以完成信号
        self.settings_inited.emit(self.settings)
    def up_part_init(self):
        self.up_part_layout = QHBoxLayout()
        self.up_part_layout.setSpacing(0)

        self.main_layout.addLayout(self.up_part_layout)

    def left_part_init(self):
        self.left_part_layout = QVBoxLayout()
        self.left_title_bar = TitleBar(self)
        self.left_part_layout.addWidget(self.left_title_bar)
        self.play_lists= PlayLists()
        self.left_part_layout.addWidget(self.play_lists)

        self.up_part_layout.addLayout(self.left_part_layout,stretch=1)

    def right_part_init(self):
        self.right_part_layout = QVBoxLayout()
        self.right_title_bar = TitleBar(self)
        self.right_part_layout.addWidget(self.right_title_bar)
        self.playlist_view = PlayListView()
        self.right_part_layout.addWidget(self.playlist_view)
        self.up_part_layout.addLayout(self.right_part_layout,stretch=3)


    def _song_info_panel_and_playercontrols_init(self):
        self.song_info_panel_and_player_controls_layout = QHBoxLayout()
        self.song_info_panel = SongInfoPanel(self)
        self.player_controls = PlayerControls(self)
        self.song_info_panel_and_player_controls_layout.addWidget(self.song_info_panel,stretch=1)
        self.song_info_panel_and_player_controls_layout.addWidget(self.player_controls,stretch=2)

        self.main_layout.addLayout(self.song_info_panel_and_player_controls_layout)

    def _settings_init(self):
        self.settings = Settings()


    def _connect_signal_and_slot(self):
        # 切换音频时动态获取音频信息
        self.player_controls.metadata_changed.connect(self.song_info_panel.on_metadata_changed)
        # 设置加载完成后通知data_manager
        self.settings_inited.connect(self.data_manager.init_with_settings)
        self.settings_inited.connect(self.play_lists.init_with_settings)
        # playlist_view中展示的歌曲双击播放
        self.playlist_view.play_selected.connect(self.player_controls.play_selected_music)
        # 切换playlist_view展示的模型
        self.data_manager.inited_with_settings.connect(self.playlist_view.change_data_model)
        self.data_manager.change_selected_model.connect(self.playlist_view.change_data_model)
        # 切换播放列表
        self.play_lists.change_playlist.connect(self.data_manager.change_model)
        # 创建播放列表
        self.play_lists.create_playlist.connect(self.data_manager.create_new_model)
