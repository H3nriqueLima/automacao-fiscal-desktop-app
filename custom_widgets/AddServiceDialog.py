from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QWidget
from PySide6.QtCore import Qt

from models.TaskMappings import SYSTEM_KEY_TO_DISPLAY_NAME


class AddServiceDialog(QDialog):

    def __init__(self, availableSystemKeys: list[str], parent: QWidget | None = None):
        super().__init__(parent)

        self.result_data: dict | None = None

        self.setWindowTitle("Adicionar Serviço")
        self.setFixedSize(300, 260)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #042e67;
                font-weight: 600;
            }
            QComboBox, QLineEdit {
                background-color: transparent;
                border: 1px solid #EEEEEE;
                border-radius: 5px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Sistema / Site"))
        self.boxSystem = QComboBox()

        self._systemKeys = availableSystemKeys
        displayNames = [SYSTEM_KEY_TO_DISPLAY_NAME.get(k, k) for k in availableSystemKeys]

        if displayNames:
            self.boxSystem.addItems(displayNames)
        else:
            self.boxSystem.addItem("Nenhum sistema disponível")
            self.boxSystem.setEnabled(False)
        layout.addWidget(self.boxSystem)

        layout.addWidget(QLabel("Login / Usuário"))
        self.inputLogin = QLineEdit()
        self.inputLogin.setPlaceholderText("Informe o login")
        layout.addWidget(self.inputLogin)

        layout.addWidget(QLabel("Senha"))
        self.inputPassword = QLineEdit()
        self.inputPassword.setPlaceholderText("Informe a senha")
        layout.addWidget(self.inputPassword)

        layout.addStretch()

        buttonsRow = QHBoxLayout()
        btnCancel = QPushButton("Cancelar")
        btnCancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btnCancel.setStyleSheet("""
            background-color: transparent;
            border: 1px solid #EEEEEE;
            border-radius: 5px;
            padding: 6px;
            color: #042e67;
        """)
        btnCancel.clicked.connect(self.reject)

        btnSave = QPushButton("Salvar")
        btnSave.setCursor(Qt.CursorShape.PointingHandCursor)
        btnSave.setStyleSheet("""
            background-color: #06adc2;
            border-radius: 5px;
            padding: 6px;
            color: white;
            font-weight: 700;
        """)
        btnSave.clicked.connect(self._onSaveClicked)

        buttonsRow.addWidget(btnCancel)
        buttonsRow.addWidget(btnSave)
        layout.addLayout(buttonsRow)

    def _onSaveClicked(self):
        if not self.boxSystem.isEnabled():
            return

        login = self.inputLogin.text().strip()
        password = self.inputPassword.text().strip()

        if not login or not password:
            return

        index = self.boxSystem.currentIndex()
        systemKey = self._systemKeys[index]

        self.result_data = {
            "system_name": systemKey,
            "login": login,
            "password": password,
        }
        self.accept()