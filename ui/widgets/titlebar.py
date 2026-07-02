import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy

from utils.assets_utils import AssetsUtils


class TitleBar(QWidget):
    def __init__(self,parent,is_left:bool):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.parent = parent
        self.mouse_pressed = False  # 用于实现窗口拖拽
        self.is_left = is_left
        self._ui_init()
        self.setObjectName('titlebar')

    def _ui_init(self):
        '''初始化UI'''
        self.main_layout = QHBoxLayout(self) # 主要布局,水平布局
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(10,0,10,0)

        if self.is_left:
            self._title_init()
        else:
            self.spacer = QSpacerItem(0,0,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
            self.main_layout.addSpacerItem(self.spacer)
            self._button_init()

    def _title_init(self):
        self.label = QLabel('Music Player')
        self.main_layout.addWidget(self.label)

    def _button_init(self):
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('close_fill.png')))
        self.close_button.setFixedSize(30,30)
        self.close_button.clicked.connect(self.parent.close)
        self.minmum_button = QPushButton()
        self.minmum_button.setIcon(QIcon(AssetsUtils.get_icon_full_path_by_asset_name('minimize_fill.png')))
        self.minmum_button.setFixedSize(30, 30)
        self.minmum_button.clicked.connect(self.parent.showMinimized)
        self.main_layout.addWidget(self.minmum_button)
        self.main_layout.addWidget(self.close_button)


    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.pos())
            # 只有点击空白区域才拖动
            if child is None or child is self.label:
                print(child)
                self.mouse_pressed = True
                self.relative_pos = (event.globalPosition().x() - self.parent.x(), event.globalPosition().y() - self.parent.y())  # 窗口和鼠标的相对坐标

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if(self.mouse_pressed):
            self.parent.move(event.globalPosition().x() - self.relative_pos[0], event.globalPosition().y() - self.relative_pos[1])

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed=False
