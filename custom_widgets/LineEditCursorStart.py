from PySide6.QtWidgets import QLineEdit


class LineEditCursorStart(QLineEdit):

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.setCursorPosition(0)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setCursorPosition(0)