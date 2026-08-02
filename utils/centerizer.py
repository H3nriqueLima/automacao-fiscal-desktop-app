from PySide6.QtWidgets import QWidget, QApplication


class WindowUtils:

    @staticmethod
    def center(window:QWidget):
        screen = QApplication.primaryScreen()

        if not screen:
            return

        screenGeometry = screen.availableGeometry()
        windowGeometry = window.frameGeometry()

        windowGeometry.moveCenter(screenGeometry.center())
        window.move(windowGeometry.topLeft())