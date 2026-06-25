'''
歌曲信息面板
'''
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QMediaMetaData
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy


class SongInfoPanel(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.metadate=None
        self.title=None
        self.artist=None
        self.album=None
        self.cover_image=None
        self._ui_init()

    def _ui_init(self):
        self.main_layout = QHBoxLayout(self)
        self._cover_init()
        self._media_info_init()

    def _media_info_init(self):
        '''歌手和歌曲名'''
        self.title_and_artist_layout = QVBoxLayout(self)
        self.title_label = QLabel(self.title)
        # Ignored 不会根据歌名长度拓宽窗口
        self.title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.title_label.setToolTip(self.title)
        self.artist_label = QLabel(self.artist)
        self.artist_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.title_and_artist_layout.addWidget(self.title_label)
        self.title_and_artist_layout.addWidget(self.artist_label)
        self.main_layout.addLayout(self.title_and_artist_layout)

    def _cover_init(self):
        '''专辑封面'''
        self.cover_label = QLabel()
        self.cover_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.cover_label.setFixedSize(100, 100)
        self.main_layout.addWidget(self.cover_label)


    @Slot()
    def on_metadata_changed(self,player:QMediaPlayer):
        self.metadate = player.metaData()

        # 歌曲名
        self.title = self.metadate.value(QMediaMetaData.Key.Title) or '未知歌曲'
        self.title_label.setText(self.title)
        self.title_label.setToolTip(self.title)

        # 歌手
        artist_raw = self.metadate.value(QMediaMetaData.Key.ContributingArtist)
        if isinstance(artist_raw, list):
            self.artist = ", ".join(str(a) for a in artist_raw)
        else:
            self.artist = str(artist_raw) if artist_raw else "未知歌手"
        self.artist_label.setText(self.artist)
        self.artist_label.setToolTip(self.artist)

        # 专辑
        self.album = self.metadate.value(QMediaMetaData.Key.AlbumTitle) or '未知专辑'

        # 封面（返回 QImage）
        cover_image = self.metadate.value(QMediaMetaData.Key.ThumbnailImage)
        if not cover_image.isNull():
            print(f"封面已加载，尺寸: {cover_image.size()}")
            origin_pixmap = QPixmap.fromImage(cover_image)
            scaled_pixmap = origin_pixmap.scaled(self.cover_label.size())
            self.cover_label.setPixmap(scaled_pixmap)
        else:
            self.cover_label.clear()
