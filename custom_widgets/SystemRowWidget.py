from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QLineEdit, QWidget, QFileDialog
from PySide6.QtCore import Qt


class SystemRowWidget(QFrame):

    def __init__(self,
                 systemName: str,
                 login: str,
                 password: str,
                 isCertificateBased: bool = False,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.systemName = systemName
        self.isCertificateBased = isCertificateBased

        self.setObjectName("SystemRow")
        self.setStyleSheet("""
            #SystemRow {
                background-color: white;
                border: 1px solid lightgray;
                border-radius: 8px;
                padding: -1px;
                margin: 2px;
            }""")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Titulo do Sistema
        systemNameColumn = QFrame()
        layoutSystemNameColumn = QHBoxLayout(systemNameColumn)
        systemNameLabel = QLabel(systemName)
        systemNameLabel.setStyleSheet("color: #182946; font-weight: 700;")
        systemNameColumn.setFixedWidth(190)
        layoutSystemNameColumn.setContentsMargins(0, 0, 0, 0)
        layoutSystemNameColumn.setSpacing(0)
        layoutSystemNameColumn.addWidget(systemNameLabel)
        layout.addWidget(systemNameColumn)

        if isCertificateBased:
            certColumn = QFrame()
            layoutCertColumn = QVBoxLayout(certColumn)
            certRow = QHBoxLayout()

            self.certField = QLineEdit(login)
            self.certField.setReadOnly(True)
            self.certField.setPlaceholderText("Selecione o certificado")
            self.certField.setStyleSheet(
                "background-color: white; border: 1px solid lightgray; border-radius: 5px; padding: 4px;")

            btnBrowse = QPushButton()
            btnBrowse.setObjectName("btnBrowseCert")
            btnBrowse.setIcon(QIcon("images/icone-Caminho-semfundo.png"))
            btnBrowse.setStyleSheet("""
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
            btnBrowse.setCursor(Qt.CursorShape.PointingHandCursor)
            btnBrowse.setFixedWidth(30)
            btnBrowse.clicked.connect(self._browseCertificate)

            certRow.addWidget(self.certField)
            certRow.addWidget(btnBrowse)

            certColumn.setFixedWidth(420)
            layoutCertColumn.setContentsMargins(9, 6, 9, 6)
            layoutCertColumn.setSpacing(0)
            layoutCertColumn.addLayout(certRow)
            layout.addWidget(certColumn)

            self.loginField = self.certField
            self.passwordField = None
        else:
            # Login do Sistema
            loginColumn = QFrame()
            layoutLoginColumn = QVBoxLayout(loginColumn)
            loginLine = QLineEdit(login)
            loginLine.setStyleSheet(
                "background-color: white; border: 1px solid lightgray; border-radius: 5px; padding: 4px;")
            loginLine.setPlaceholderText("Login/Usuário")
            loginColumn.setFixedWidth(210)
            layoutLoginColumn.setContentsMargins(9, 6, 9, 6)
            layoutLoginColumn.setSpacing(0)
            layoutLoginColumn.addWidget(loginLine)
            layout.addWidget(loginColumn)

            # Senha
            passwordColumn = QFrame()
            layoutPasswordColumn = QVBoxLayout(passwordColumn)
            passwordLine = QLineEdit(password)
            passwordLine.setStyleSheet(
                "background-color: white; border: 1px solid lightgray; border-radius: 5px; padding: 4px;")
            passwordColumn.setFixedWidth(210)
            layoutPasswordColumn.setContentsMargins(9, 6, 9, 6)
            layoutPasswordColumn.setSpacing(0)
            layoutPasswordColumn.addWidget(passwordLine)
            layout.addWidget(passwordColumn)

            self.loginField = loginLine
            self.passwordField = passwordLine

    def _browseCertificate(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Certificado", "", "Certificado Digital (*.pfx *.p12)"
        )
        if path:
            self.certField.setText(path)

    # GETTERS
    def getSystemName(self) -> str:
        return self.systemName

    def getLogin(self) -> str:
        return self.loginField.text()

    def getPassword(self) -> str:
        return self.passwordField.text() if self.passwordField else ""