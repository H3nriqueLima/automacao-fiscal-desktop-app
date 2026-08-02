from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class ListWidgetCheck(QListWidget):

    def __init__(self, options: list[str]) -> None:
        super().__init__()
        self.options = options

        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)

        self.setObjectName("ListWidgetCheck")
        self.setStyleSheet("""
            #ListWidgetCheck {
                border: None;
                color: #042e67;
            }
            
            #ListWidgetCheck::item:hover {
                background-color: #EEEEEE;
            }
            
            #ListWidgetCheck::item:selected {
                background-color: #EEEEEE;
                color: #042e67;
            }
        """)
        self.setSpacing(4)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        for text in options:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.addItem(item)

        self.itemClicked.connect(self.toggleCheck)

    @staticmethod
    def toggleCheck(item: QListWidgetItem):
        newState = (
            Qt.CheckState.Unchecked
            if item.checkState() == Qt.CheckState.Checked
            else Qt.CheckState.Checked
        )
        item.setCheckState(newState)