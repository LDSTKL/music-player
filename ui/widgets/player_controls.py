'''
播放控制栏
'''
import random
import sys
import PySide6.QtGui
from PySide6.QtGui import QIcon
from PySide6.QtCore import QUrl, Slot, Qt, Signal, QPoint, QSize
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QStyle, \
    QStyleOptionSlider, QMenu, QWidgetAction, QLabel, QSpacerItem, QSizePolicy

from utils.assets_utils import AssetsUtils
from utils.database_utils import DataBaseUtils
from utils.settings_utils import SettingsUtils


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
        if self.orientation() ==Qt.Orientation.Horizontal:
            self.handle_width = handle_rect.width()  # 获取滑块宽度
            self.true_length = self.width() - self.handle_width  # 获取滑动条真实长度
            event_position = event.position()
            # 滑块位置移动到鼠标位置
            self.setValue(self.minimum()+int((self.maximum() - self.minimum()) *(event_position.x()-self.handle_width/2)/self.true_length))
            super().mousePressEvent(event)
        else:
            self.handle_width = handle_rect.height()
            self.true_length = self.height() - self.handle_width
            event_position = event.position()
            # 滑块位置移动到鼠标位置
            self.setValue(self.minimum() + int((self.maximum() - self.minimum()) * (self.true_length - event_position.y() + self.handle_width / 2) / self.true_length))
            super().mousePressEvent(event)

class VolumeWidget(QWidget):
    def __init__(self,parent =None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.volume_value = QLabel(str(SettingsUtils.get_settings()['volume']))
        self.volume_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_slider = EnhancedSlider(Qt.Orientation.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(SettingsUtils.get_settings()['volume'])
        self.volume_slider.setFixedHeight(100)
        self.volume_slider.setFixedWidth(20)

        self.volume_slider.valueChanged.connect(lambda v:self.volume_value.setText(str(v)))
        self.volume_slider.sliderReleased.connect(self._update_settings)
        self.main_layout.addWidget(self.volume_value)
        self.main_layout.addWidget(self.volume_slider)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    @Slot()
    def _update_settings(self):
        conn = DataBaseUtils.get_new_connection()
        DataBaseUtils.update_settings(conn,volume = self.volume_slider.value())


class PlayerControls(QWidget):
    metadata_changed = Signal(QMediaPlayer)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.music_list = []
        self.curr_music_index = 0
        self.play_modes = ['repeat_line.png','repeat_line.png','repeat_one_line.png','shuffle_line.png']
        self.play_mode = SettingsUtils.get_settings()['play_mode']
        self._ui_init()
        self._player_init()
        self._volume_slider_init()
        self._connect_slot()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)





    def _ui_init(self):
        self.main_layout = QVBoxLayout(self)  # 加上self自动应用到父组件
        self._controls_init()
        self._slider_init()

    def _controls_init(self):
        '''音乐控制'''
        self.controls_layout = QHBoxLayout() # 布局
        self.pause_button = QPushButton(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('pause_line.png')),'')
        self.pause_button.hide()
        self.play_button = QPushButton(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('play_line.png')),'')
        self.prev_media_button = QPushButton(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('skip_previous_line.png')),'')
        self.next_media_button = QPushButton(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('skip_forward_line.png')),'')
        self.volume_button = QPushButton(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('volume_line.png')),'')
        self.play_mode_button = QPushButton()
        self.change_play_mode(True)

        self.pause_button.setFixedSize(48,48)
        self.play_button.setFixedSize(48,48)
        self.prev_media_button.setFixedSize(36,36)
        self.next_media_button.setFixedSize(36,36)
        self.volume_button.setFixedSize(36,36)
        self.play_mode_button.setFixedSize(36,36)

        self.play_button.setIconSize(QSize(48, 48))
        self.pause_button.setIconSize(QSize(48, 48))

        self.pause_button.setObjectName('player_control_button')
        self.play_button.setObjectName('player_control_button')
        self.prev_media_button.setObjectName('player_control_button')
        self.next_media_button.setObjectName('player_control_button')
        self.volume_button.setObjectName('player_control_button')
        self.play_mode_button.setObjectName('player_control_button')

        self.spacer = QSpacerItem(0,0,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Maximum)

        self.controls_layout.addSpacerItem(self.spacer)
        self.controls_layout.addWidget(self.play_mode_button)
        self.controls_layout.addWidget(self.prev_media_button)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.next_media_button)
        self.controls_layout.addWidget(self.volume_button)
        self.controls_layout.addSpacerItem(self.spacer)

        self.main_layout.addLayout(self.controls_layout)

    def _slider_init(self):
        '''音乐进度条'''
        self.slider= EnhancedSlider(Qt.Orientation.Horizontal)
        self.slider.setSingleStep(1000) # 使用音乐的毫秒数设置进度条的范围,默认的步长为1太小
        self.slider.setPageStep(10000) # 设置后键盘上左右箭头和pageUp,pageDown效果正常了

        self.main_layout.addWidget(self.slider)

    def _volume_slider_init(self):
        '''音量控制条'''
        self.volume_menu = QMenu()
        self.volume_menu.setStyleSheet('''
                    background-color: #656564;
                    color: white;''')
        self.volume_widget = VolumeWidget()
        self.volume_widget.setStyleSheet('''
        QSlider::groove:vertical {
            width: 4px;
            background-color: #333333;  /* 轨道背景 */
            border-radius: 2px;
        }
        
        QSlider::sub-page:vertical {
            background-color: transparent;  /* 上方透明 */
        }
        
        QSlider::add-page:vertical {
            background-color: #2ABf9E;  /* 下方有色 */
        }
        
        QSlider::handle:vertical {
            height: 12px;
            width: 12px;
            margin: 0 -4px;  /* 让滑块水平居中并突出 */
            background-color: #FFFFFF;
            border-radius: 6px;
        }
        
        QSlider::handle:vertical:hover {
            background-color: #EEEEEE;
        }
        ''')
        self.volume_widget_action = QWidgetAction(self.volume_menu)
        self.volume_widget_action.setDefaultWidget(self.volume_widget)
        self.volume_menu.addAction(self.volume_widget_action)



    def _player_init(self):
        '''媒体播放器'''
        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.audioOutput.setVolume(SettingsUtils.get_settings()['volume']/100)
        # QMediaPlayer 是异步加载媒体,此时获取duration()为0,因此需要利用durationChanged信号
        # 而且利用信号,对后续切换音乐的功能开发奠定了基础


    def _connect_slot(self):
        # 绑定按钮功能
        self.pause_button.clicked.connect(self.pause)
        self.play_button.clicked.connect(self.play)
        self.next_media_button.clicked.connect(self.play_next)
        self.prev_media_button.clicked.connect(self.play_prev)
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
        self.player.mediaStatusChanged.connect(self.media_status_changed) # 音乐播放结束后续操作
        self.player.metaDataChanged.connect(lambda :self.metadata_changed.emit(self.player))

        self.volume_widget.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_button.clicked.connect(self._show_volume_menu)

        self.play_mode_button.clicked.connect(self.change_play_mode)


    @Slot()
    def pause(self):
        '''暂停'''
        self.player.pause()
        self.play_button.show()
        self.pause_button.hide()

    @Slot()
    def play(self):
        '''播放'''
        self.player.play()
        self.pause_button.show()
        self.play_button.hide()


    def play_random(self):
        '''播放'''
        self.player.setSource(QUrl.fromLocalFile(random.choice(self.music_list)))
        self.play()

    @Slot()
    def play_next(self):
        '''下一首'''
        if self.play_mode == 3:
            self.play_random()
        else:
            self.curr_music_index = (self.curr_music_index+1)% len(self.music_list)
            self.player.setSource(QUrl.fromLocalFile(self.music_list[self.curr_music_index]) )
            self.play()

    @Slot()
    def play_prev(self):
        '''上一首'''
        if self.play_mode == 3:
            self.play_random()
        else:
            self.curr_music_index = (self.curr_music_index-1)% len(self.music_list)
            self.player.setSource(QUrl.fromLocalFile(self.music_list[self.curr_music_index]))
            self.play()

    @Slot()
    def update_slider_when_position_changed(self,p):
        '''音乐播放时，滑块移动，实现进度条效果'''
        # 如果用户在拖动滑块,就不随着媒体播放更新滑块,避免滑块乱跳
        if not self.slider.isSliderDown():
            self.slider.setValue(p)

    @Slot()
    def update_player_when_slider_released(self):
        '''用户释放滑块后调整音乐播放进度'''
        self.player.setPosition(self.slider.value())


    @Slot()
    def media_status_changed(self,status:QMediaPlayer.MediaStatus):
        '''处理播放结束后后续操作,与播放方式有关'''
        if status==QMediaPlayer.MediaStatus.EndOfMedia:
            if self.play_mode == 0:
                self.pause()
            elif self.play_mode ==1:
                self.play_next()
            elif self.play_mode == 2:
                self.play()
            elif self.play_mode ==3:
                self.play_random()

    @Slot()
    def play_selected_music(self,path:str,music_list:list[str]):
        '''此信号用于播放列表双击播放时'''
        # 记录当前播放歌曲在列表中的下标
        for index,file_path in enumerate(music_list) :
            if path == file_path:
                self.curr_music_index = index
        self.music_list=music_list
        self.player.setSource(QUrl.fromLocalFile(path))
        self.play()

    @Slot()
    def on_volume_changed(self,value:int):
        self.audioOutput.setVolume(value/100)

    @Slot()
    def _show_volume_menu(self):
        # 获取菜单的建议大小（确保高度准确）
        menu_size = self.volume_menu.sizeHint()

        # 计算位置：
        # x: 按钮中心 - 菜单宽度的一半 (实现水平居中)
        # y: 按钮顶部 - 菜单高度 (实现在按钮上方显示)
        pos = self.volume_button.mapToGlobal(QPoint(
            self.volume_button.width() / 2 - menu_size.width() / 2,
            -menu_size.height()
        ))

        self.volume_menu.exec(pos)



    @Slot()
    def change_play_mode(self,is_init:bool = False):
        if not is_init:
            self.play_mode = (self.play_mode+1) % len(self.play_modes)
        self.play_mode_button.setIcon(QIcon(AssetsUtils.get_icon_full_path_by_asset_name(self.play_modes[self.play_mode])))
        if self.play_mode != 0:
            self.play_mode_button.setStyleSheet('''
                QPushButton {
                    background-color: #26211e;
                }
                QPushButton:hover {
                    background-color: #858585;
                }''')
            if self.play_mode==1: self.play_mode_button.setToolTip('循环播放')
            if self.play_mode==2: self.play_mode_button.setToolTip('单曲循环')
            if self.play_mode==3: self.play_mode_button.setToolTip('随机播放')
        else:
            self.play_mode_button.setStyleSheet('''
                QPushButton {
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #858585;
                }''')
            self.play_mode_button.setToolTip('循环关闭')
        conn = DataBaseUtils.get_new_connection()
        DataBaseUtils.update_settings(conn,play_mode = self.play_mode)





if __name__ == '__main__':
    app = QApplication()
    window = EnhancedSlider(Qt.Orientation.Vertical)
    window.show()
    sys.exit(app.exec())