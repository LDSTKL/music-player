'''
播放控制栏
'''
import sys

import PySide6.QtGui
from PySide6.QtCore import QUrl, Slot, Qt, QPoint, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QStyle, \
    QStyleOptionSlider

from ui.widgets.song_info_panel import SongInfoPanel


class EnhancedSlider(QSlider):
    '''
    实现鼠标点击滑动条，滑块跳转到对应位置：
    滑块的有效移动距离 不等于 滑动条的长度，因为滑块自身有一定宽度
    滑块能移动的距离 = 滑动条的长度 - 滑块的宽度
    用户点击滑动条的位置，转换为该位置对应的值 = 
    (事件横坐标 - 1/2滑块的宽度  /  滑块能移动的距离) * 滑动条表示的值的范围 + 滑动条起始值
    '''
    def __init__(self,orientation:Qt.Orientation.Horizontal):
        super().__init__(orientation)
        # 创建选项对象
        self.option = QStyleOptionSlider()

        
    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        self.option.initFrom(self)
        self.option.orientation = self.orientation()
        self.option.minimum = self.minimum()
        self.option.maximum = self.maximum()
        self.option.sliderPosition = self.sliderPosition()

        # 正确调用：cc, opt, sc, widget
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,  # cc
            self.option,  # opt
            QStyle.SubControl.SC_SliderHandle,  # sc
            self  # w
        )

        self.handle_width = handle_rect.width()  # 获取滑块宽度
        self.true_length = self.width() - self.handle_width  # 获取滑动条真实长度
        event_position = event.position()
        # 滑块位置移动到鼠标位置
        self.setValue(self.minimum()+int((self.maximum() - self.minimum()) *(event_position.x()-self.handle_width/2)/self.true_length))
        super().mousePressEvent(event)




class PlayerControls(QWidget):
    metadata_changed = Signal(QMediaPlayer)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.slider_is_pressed =False
        self.music_list = [r'D:\音乐\周杰伦 - 爱琴海.mp3',r'D:\音乐\许嵩 - 如果当时.mp3']
        self._ui_init()
        self._player_init()
        self._connect_slot()





    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)  # 加上self自动应用到父组件
        self._controls_init()
        self._slider_init()

    def _controls_init(self):
        '''音乐控制'''
        self.controls_layout = QHBoxLayout() # 布局
        self.pause_button = QPushButton('||')
        self.pause_button.hide()
        self.pause_button.clicked.connect(self.pause)
        self.play_button = QPushButton('>')
        self.play_button.clicked.connect(self.play)
        self.next_media_button = QPushButton('>>')
        self.next_media_button.clicked.connect(lambda :self.player.setSource(QUrl.fromLocalFile(self.music_list[1])))
        self.prev_media_button = QPushButton('<<')
        self.prev_media_button.clicked.connect(lambda: self.player.setSource(QUrl.fromLocalFile(self.music_list[0])))
        self.volume_button = QPushButton('🔉')
        self.play_mode_button = QPushButton('o')


        self.controls_layout.addWidget(self.play_mode_button)
        self.controls_layout.addWidget(self.prev_media_button)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.next_media_button)
        self.controls_layout.addWidget(self.volume_button)

        self.main_layout.addLayout(self.controls_layout)

    def _slider_init(self):
        '''音乐进度条'''
        self.slider= EnhancedSlider(Qt.Orientation.Horizontal)
        self.slider.setSingleStep(1000) # 使用音乐的毫秒数设置进度条的范围,默认的步长为1太小
        self.slider.setPageStep(10000) # 设置后键盘上左右箭头和pageUp,pageDown效果正常了

        self.main_layout.addWidget(self.slider)

    def _player_init(self):
        '''媒体播放器'''
        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.setSource(QUrl.fromLocalFile(self.music_list[0]))
        self.audioOutput.setVolume(0.5)
        # QMediaPlayer 是异步加载媒体,此时获取duration()为0,因此需要利用durationChanged信号
        # 而且利用信号,对后续切换音乐的功能开发奠定了基础


    def _connect_slot(self):
        # 绑定媒体播放器和音乐进度条
        self.player.durationChanged.connect(lambda d: self.slider.setRange(0, d))
        self.player.positionChanged.connect(self.update_slider_when_position_changed)
        self.slider.sliderReleased.connect(self.update_player_when_slider_released)
        # self.slider.valueChanged.connect(lambda v: self.player.setPosition(v))
        # 不能用valueChanged,会和self.player.positionChanged出现循环更新的情况
        '''
        由于在同一个线程中,信号和槽使用ConnectionType为DirectConnection:信号发射时，立即在发送者线程中直接调用槽函数
        因此逻辑一定是以下情况：
        positionChanged信号发出—>执行update_slider(修改slider失败)—>
        sliderReleased信号发出(isSliderDown()变为false)—>执行update_player—>
        positionChanged信号发出—>执行update_slider(修改slider成功)
        不存在：
        positionChanged信号发出—>sliderReleased信号发出(isSliderDown()变为false)—>
        执行update_slider(修改slider成功)—>执行update_player
        即用户修改丢失
        '''
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        self.player.metaDataChanged.connect(lambda :self.metadata_changed.emit(self.player))


    @Slot()
    def pause(self):
        self.player.pause()
        self.play_button.show()
        self.pause_button.hide()

    @Slot()
    def play(self):
        self.player.play()
        self.pause_button.show()
        self.play_button.hide()

    @Slot()
    def update_slider_when_position_changed(self,p):
        '''如果用户在拖动滑块,就不随着媒体播放更新滑块,避免滑块乱跳'''
        if not self.slider.isSliderDown():
            self.slider.setValue(p)

    @Slot()
    def update_player_when_slider_released(self):
        self.player.setPosition(self.slider.value())

    @Slot()
    def media_status_changed(self,status:QMediaPlayer.MediaStatus):
        if status==QMediaPlayer.MediaStatus.EndOfMedia:
            self.pause()

    @Slot()
    def play_selected_music(self,path:str):
        self.player.setSource(QUrl.fromLocalFile(path))
        self.play()




if __name__ == '__main__':
    app = QApplication()
    window = PlayerControls()
    window.show()
    sys.exit(app.exec())