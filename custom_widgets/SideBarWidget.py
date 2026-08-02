from PySide6.QtWidgets import QWidget, QStyleOption, QStyle
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt


class SideBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pixmap = QPixmap("images/fundo-lateral.png")

    def paintEvent(self, event):
        painter = QPainter(self)

        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            x = (scaled.width() - self.width()) / 2
            y = (scaled.height() - self.height()) / 2
            painter.drawPixmap(-int(x), -int(y), scaled)

        super().paintEvent(event)