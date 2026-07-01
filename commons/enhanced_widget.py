from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QColor
from PySide6.QtWidgets import QTableView


class HoverTableModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_row = -1

    def set_hover_row(self, row):
        old_row = self.hover_row
        self.hover_row = row
        # 刷新旧行和新行
        if old_row >= 0:
            self.dataChanged.emit(self.index(old_row, 0), self.index(old_row, self.columnCount() - 1))
        if row >= 0:
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundRole and index.row() == self.hover_row:
            return QColor(220, 220, 220)  # hover 背景色
        return super().data(index, role)


class HoverProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_row = -1

    def set_hover_row(self, row):
        old_row = self.hover_row
        self.hover_row = row

        # 获取列数
        cols = self.columnCount()
        if cols == 0: return

        # 刷新旧行
        if old_row >= 0 and old_row < self.rowCount():
            top_left = self.index(old_row, 0)
            bottom_right = self.index(old_row, cols - 1)
            self.dataChanged.emit(top_left, bottom_right)

        # 刷新新行
        if row >= 0 and row < self.rowCount():
            top_left = self.index(row, 0)
            bottom_right = self.index(row, cols - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # 注意：这里的 index 是 Proxy 的 index
        if role == Qt.ItemDataRole.BackgroundRole and index.row() == self.hover_row:
            return QColor('#333333')

        # 其他情况交给父类处理（会自动映射到 Source Model）
        return super().data(index, role)

class HoverTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        index = self.indexAt(event.position().toPoint())
        row = index.row() if index.isValid() else -1

        model = self.model()
        if isinstance(model, HoverProxyModel) and model.hover_row != row:
            model.set_hover_row(row)
        elif isinstance(model, HoverTableModel) and model.hover_row != row:
            model.set_hover_row(row)