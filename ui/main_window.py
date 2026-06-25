import PySide6
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel

from ui.widgets.player_controls import PlayerControls
from ui.widgets.playlist_view import PlayListView
from ui.widgets.settings import Settings
from ui.widgets.song_info_panel import SongInfoPanel
from ui.widgets.titlebar import TitleBar


class MainWindow(QWidget):
    settings_inited = Signal(Settings)

    def __init__(self):
        super().__init__()
        self._window_init()
        self._ui_init()

    def _window_init(self):
        '''初始化窗体'''
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.resize(800, 500)

    def _ui_init(self):
        '''初始化UI'''
        self.main_layout = QVBoxLayout(self)  # 主要布局,垂直布局
        self._titlebar_init()
        self._playlist_view_init()
        self._song_info_panel_and_playercontrols_init()

        self._settings_init()
        self._connect_signal_and_slot()

        # 发送设置以完成信号
        self.settings_inited.emit(self.settings)



    def _titlebar_init(self):
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

    def _song_info_panel_and_playercontrols_init(self):
        self.song_info_panel_and_player_controls_layout = QHBoxLayout()
        self.song_info_panel = SongInfoPanel(self)
        self.player_controls = PlayerControls(self)
        self.song_info_panel_and_player_controls_layout.addWidget(self.song_info_panel,stretch=1)
        self.song_info_panel_and_player_controls_layout.addWidget(self.player_controls,stretch=2)

        self.main_layout.addLayout(self.song_info_panel_and_player_controls_layout)

    def _settings_init(self):
        self.settings = Settings()


    def _playlist_view_init(self):
        self.playlist_view = PlayListView()
        self.main_layout.addWidget(self.playlist_view)

    def _connect_signal_and_slot(self):
        # 切换音频时动态获取音频信息
        self.player_controls.metadata_changed.connect(self.song_info_panel.on_metadata_changed)
        #
        self.settings_inited.connect(self.playlist_view.init_with_settings)
        #
        self.playlist_view.play_selected.connect(self.player_controls.play_selected_music)
