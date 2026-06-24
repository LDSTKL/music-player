import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy


class TitleBar(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent = parent
        self.mouse_pressed = False  # 用于实现窗口拖拽
        self._ui_init()

    def _ui_init(self):
        '''初始化UI'''
        self.main_layout = QHBoxLayout(self) # 主要布局,水平布局
        self._title_init()
        self._button_init()

    def _title_init(self):
        self.label = QLabel('hello world')
        self.main_layout.addWidget(self.label)

    def _button_init(self):
        self.close_button = QPushButton('x')
        self.close_button.clicked.connect(self.parent.close)
        self.minmum_button = QPushButton('-')
        self.minmum_button.clicked.connect(self.parent.showMinimized)
        self.main_layout.addWidget(self.minmum_button)
        self.main_layout.addWidget(self.close_button)


    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.pos())
            # 只有点击空白区域才拖动
            if child is None:
                self.mouse_pressed = True
                self.relative_pos = (event.globalPosition().x() - self.parent.x(), event.globalPosition().y() - self.parent.y())  # 窗口和鼠标的相对坐标

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if(self.mouse_pressed):
            self.parent.move(event.globalPosition().x() - self.relative_pos[0], event.globalPosition().y() - self.relative_pos[1])

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed=False
