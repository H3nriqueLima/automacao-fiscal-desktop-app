from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class ScaledImageLabel(QLabel):
    def __init__(self, parent=None, path=None, keep_ratio=Qt.AspectRatioMode.KeepAspectRatio):
        super().__init__(parent)
        self._original_pixmap = QPixmap(path) if path else QPixmap()
        self._keep_ratio = keep_ratio
        self.setMinimumSize(1, 1)

    def setImage(self, path):
        self._original_pixmap = QPixmap(path)
        self._update_scaled()

    def setPixmapOriginal(self, pixmap: QPixmap):
        self._original_pixmap = pixmap
        self._update_scaled()

    def _update_scaled(self):
        if self._original_pixmap.isNull():
            return
        scaled = self._original_pixmap.scaled(
            self.size(),
            self._keep_ratio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        self._update_scaled()
        super().resizeEvent(event)