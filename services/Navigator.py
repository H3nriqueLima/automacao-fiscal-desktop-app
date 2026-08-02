from PySide6.QtWidgets import QStackedWidget, QWidget


class Navigator:
    def __init__(self, stackedWidget:QStackedWidget) -> None:
        self.stack_widget = stackedWidget

    def openPage(self, page:QWidget):
        self.stack_widget.setCurrentWidget(page)