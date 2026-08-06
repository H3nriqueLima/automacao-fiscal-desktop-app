from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QScrollArea, QFrame
from PySide6.QtCore import Qt


class RunningTasksDialog(QDialog):

    def __init__(self, monitor, parent: QWidget | None = None):
        super().__init__(parent)
        self.monitor = monitor

        self.setWindowTitle("Automações em Execução")
        self.setFixedSize(360, 320)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #042e67; }
        """)

        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.container = QWidget()
        self.listLayout = QVBoxLayout(self.container)
        self.listLayout.setSpacing(8)
        scroll.setWidget(self.container)

        outerLayout.addWidget(scroll)

        self.monitor.taskListChanged.connect(self._refresh)
        self._refresh()

    def _refresh(self):
        while self.listLayout.count():
            item = self.listLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entries = self.monitor.getAll()

        if not entries:
            self.listLayout.addWidget(QLabel("Nenhuma automação em execução."))
            return

        for entry in entries:
            row = QFrame()
            row.setStyleSheet("border: 1px solid #EEEEEE; border-radius: 6px; padding: 6px;")
            rowLayout = QHBoxLayout(row)

            info = QLabel(f"{entry['label']}\n{entry['status']}")
            rowLayout.addWidget(info)

            if entry["status"] == "Em andamento":
                btnStop = QPushButton("Parar")
                btnStop.setCursor(Qt.CursorShape.PointingHandCursor)
                btnStop.clicked.connect(lambda _, eid=entry["id"]: self.monitor.stop(eid))
                rowLayout.addWidget(btnStop)

        self.listLayout.addStretch()