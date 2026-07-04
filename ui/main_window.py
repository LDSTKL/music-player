
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizeGrip
from ui.widgets.data_manager import DataManager
from ui.widgets.play_lists import PlayLists
from ui.widgets.player_controls import PlayerControls
from ui.widgets.playlist_view import PlayListView
from ui.widgets.settings import Settings
from ui.widgets.song_info_panel import SongInfoPanel
from ui.widgets.titlebar import TitleBar
from utils.database_utils import DataBaseUtils


class MainWindow(QWidget):
    settings_inited = Signal(str)

    def __init__(self):
        super().__init__()
        self._database_init() # 数据库初始化
        self._data_manager_init()
        self._settings_init()
        self._window_init() # 窗体初始化
        self._ui_init() # 窗体内UI初始化
        self.setObjectName('main_window')
        self.setProperty("theme", "dark")
        self._connect_signal_and_slot()
        # 发送设置已经初始化完成信号
        self.settings_inited.emit(self.settings.setting_scan_dir_lineedit.text())


    def _database_init(self):
        DataBaseUtils.init_database()

    def _data_manager_init(self):
        self.data_manager = DataManager()

    def _window_init(self):
        '''初始化窗体'''
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(800, 500)
        self.resize(800, 500)

    def _ui_init(self):
        '''初始化UI'''
        self.main_layout = QVBoxLayout(self)  # 主要布局,垂直布局
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.up_part_init()
        self.left_part_init()
        self.right_part_init()
        self._song_info_panel_and_playercontrols_init()
        self._size_grip_init()



    def up_part_init(self):
        '''左上角+右上角UI初始化'''
        self.up_part_layout = QHBoxLayout()
        self.up_part_layout.setSpacing(0)
        self.up_part_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addLayout(self.up_part_layout)

    def left_part_init(self):
        '''左上角部分UI初始化'''
        self.left_part_layout = QVBoxLayout()
        self.left_part_layout.setSpacing(0)
        self.left_part_layout.setContentsMargins(0,0,0,0)

        self.left_title_bar = TitleBar(self,True)
        self.left_part_layout.addWidget(self.left_title_bar)
        self.play_lists= PlayLists(self.settings,self)
        self.left_part_layout.addWidget(self.play_lists)

        self.up_part_layout.addLayout(self.left_part_layout,stretch=1)

    def right_part_init(self):
        '''右上角部分UI初始化'''
        self.right_part_layout = QVBoxLayout()
        self.right_part_layout.setSpacing(0)
        self.right_part_layout.setContentsMargins(0, 0, 0, 0)

        self.right_title_bar = TitleBar(self,False)
        self.right_part_layout.addWidget(self.right_title_bar)
        self.playlist_view = PlayListView()

        self.right_part_layout.addWidget(self.playlist_view)
        self.up_part_layout.addLayout(self.right_part_layout,stretch=3)


    def _song_info_panel_and_playercontrols_init(self):
        self.song_info_panel_and_player_controls_layout = QHBoxLayout()
        self.song_info_panel_and_player_controls_layout.setSpacing(0)
        self.song_info_panel_and_player_controls_layout.setContentsMargins(0,0,0,0)
        self.song_info_panel = SongInfoPanel(self)

        self.player_controls = PlayerControls(self)

        self.song_info_panel_and_player_controls_layout.addWidget(self.song_info_panel,stretch=1)
        self.song_info_panel_and_player_controls_layout.addWidget(self.player_controls,stretch=2)

        self.main_layout.addLayout(self.song_info_panel_and_player_controls_layout)

    def _size_grip_init(self):
        self.size_grip = QSizeGrip(self)
        self.size_grip.resize(20, 20)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def resizeEvent(self, event):
        # 保持 size_grip 在右下角
        self.size_grip.move(self.width() - 20, self.height() - 20)
        self.play_lists.update_list_height()
        super().resizeEvent(event)

    def _settings_init(self):
        self.settings = Settings()



    def _connect_signal_and_slot(self):
        # 切换音频时动态获取音频信息
        self.player_controls.metadata_changed.connect(self.song_info_panel.on_metadata_changed)

        # 切换playlist_view展示的模型
        self.data_manager.inited_with_settings.connect(self.playlist_view.change_data_model) # 启动应用后首次设置model
        self.data_manager.change_selected_model.connect(self.playlist_view.change_data_model)
        self.data_manager.delete_playlist_finished.connect(self.playlist_view.init_add_to_playlist_actions)  # 删除歌单后更新上下文菜单
        # 搜索音乐
        self.play_lists.search_music.connect(self.data_manager.change_search_music_model)
        # 切换播放列表
        self.play_lists.change_playlist.connect(self.data_manager.change_model)
        # 创建播放列表
        self.play_lists.create_playlist_finished.connect(self.data_manager.create_new_custom_model) # 创建具体的代理模型
        self.play_lists.create_playlist_finished.connect(self.playlist_view.init_add_to_playlist_actions) # 更新上下文菜单,增加新歌单的选项
        self.play_lists.delete_playlist_finished.connect(self.data_manager.delete_a_custom_model) # 删除相应代理模型


        # playlist_view中展示的歌曲双击播放
        self.playlist_view.play_selected.connect(self.player_controls.play_selected_music)
        # 添加歌曲到指定播放列表
        self.playlist_view.add_to_playlist.connect(self.data_manager.add_to_a_playlist)
        # 从播放列表中移除歌曲
        self.playlist_view.remove_from_playlist.connect(self.data_manager.remove_from_a_playlist)

        # 设置加载完成后通知data_manager
        self.settings_inited.connect(self.data_manager.init_with_settings) # 启动应用后首次初始化
        self.settings.scan_dir_changed.connect(self.data_manager.init_with_changed_settings)
        self.settings.scan_dir_changed.connect(self.play_lists.init_with_changed_settings) # 切换目录原来的歌单也清除掉
