from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QWidget, QFileDialog
from PySide6.QtCore import Qt

from models.TaskMappings import SYSTEM_KEY_TO_DISPLAY_NAME, CERTIFICATE_BASED_SYSTEM_KEYS


class AddServiceDialog(QDialog):

    def __init__(self, availableSystemKeys: list[str], parent: QWidget | None = None):
        super().__init__(parent)

        self.result_data: dict | None = None
        self._systemKeys = availableSystemKeys

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

        displayNames = [SYSTEM_KEY_TO_DISPLAY_NAME.get(k, k) for k in availableSystemKeys]

        if displayNames:
            self.boxSystem.addItems(displayNames)
        else:
            self.boxSystem.addItem("Nenhum sistema disponível")
            self.boxSystem.setEnabled(False)
        layout.addWidget(self.boxSystem)

        self.labelLogin = QLabel("Login / Usuário")
        self.inputLogin = QLineEdit()
        self.inputLogin.setPlaceholderText("Informe o login")
        layout.addWidget(self.labelLogin)
        layout.addWidget(self.inputLogin)

        self.labelSecondField = QLabel("Senha")
        layout.addWidget(self.labelSecondField)

        self.inputPassword = QLineEdit()
        self.inputPassword.setPlaceholderText("Informe a senha")

        certRow = QHBoxLayout()
        self.btnBrowseCert = QPushButton()
        self.btnBrowseCert.setObjectName("btnBrowseCert")
        self.btnBrowseCert.setIcon(QIcon("images/icone-Caminho-semfundo.png"))
        self.btnBrowseCert.setStyleSheet("""
            #btnBrowseCert {
                background-color: transparent;
                border: 1px solid #EEEEEE;
                border-radius: 5px;
                padding: 4px;
                color: #042e67;
                font-weight: 600;
            }

            #btnBrowseCert:hover {
                background-color: #EEEEEE;
            }
        """)
        self.btnBrowseCert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnBrowseCert.setFixedWidth(32)
        self.btnBrowseCert.clicked.connect(self._browseCertificate)
        certRow.addWidget(self.inputPassword)
        certRow.addWidget(self.btnBrowseCert)
        layout.addLayout(certRow)

        self.btnBrowseCert.setVisible(False)

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

        self.boxSystem.currentIndexChanged.connect(self._onSystemChanged)
        self._onSystemChanged()  # aplica o estado certo já na abertura

    def _currentSystemKey(self) -> str | None:
        if not self.boxSystem.isEnabled():
            return None
        index = self.boxSystem.currentIndex()
        if index < 0 or index >= len(self._systemKeys):
            return None
        return self._systemKeys[index]

    def _onSystemChanged(self):
        key = self._currentSystemKey()
        usesCertificate = key in CERTIFICATE_BASED_SYSTEM_KEYS if key else False

        if usesCertificate:
            self.labelLogin.setVisible(False)
            self.inputLogin.setVisible(False)

            self.labelSecondField.setText("Certificado")
            self.inputPassword.setPlaceholderText("Selecione o certificado")
            self.inputPassword.setReadOnly(True)
            self.btnBrowseCert.setVisible(True)
        else:
            self.labelLogin.setVisible(True)
            self.inputLogin.setVisible(True)

            self.labelSecondField.setText("Senha")
            self.inputPassword.setPlaceholderText("Informe a senha")
            self.inputPassword.setReadOnly(False)
            self.btnBrowseCert.setVisible(False)

    def _browseCertificate(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Certificado", "", "Certificado Digital (*.pfx *.p12)"
        )
        if path:
            self.inputPassword.setText(path)

    def _onSaveClicked(self):
        systemKey = self._currentSystemKey()
        if systemKey is None:
            return

        usesCertificate = systemKey in CERTIFICATE_BASED_SYSTEM_KEYS
        secondValue = self.inputPassword.text().strip()

        if usesCertificate:
            if not secondValue:
                return
            self.result_data = {
                "system_name": systemKey,
                "login": secondValue,
                "password": "",
            }
        else:
            login = self.inputLogin.text().strip()
            if not login or not secondValue:
                return
            self.result_data = {
                "system_name": systemKey,
                "login": login,
                "password": secondValue,
            }

        self.accept()