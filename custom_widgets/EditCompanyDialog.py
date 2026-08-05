from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog, QFrame, QScrollArea
from PySide6.QtCore import Qt

from models.TaskMappings import SYSTEM_KEY_TO_DISPLAY_NAME, CERTIFICATE_BASED_SYSTEM_KEYS


class EditCompanyDialog(QDialog):

    FIELD_STYLE = """
        background-color: white;
        border: 1px solid #EEEEEE;
        border-radius: 5px;
        padding: 4px;
    """

    def __init__(self, company: dict, parent: QWidget | None = None):
        super().__init__(parent)

        self.company = company
        self.result_data: dict | None = None
        self._serviceFields: dict[str, dict] = {}

        self.setWindowTitle("Editar Empresa")
        self.setFixedSize(340, 480)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #042e67; font-weight: 600; }
        """)

        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(16, 16, 16, 16)
        outerLayout.setSpacing(10)

        outerLayout.addWidget(QLabel("Razão Social"))
        self.inputName = QLineEdit(company.get("name", ""))
        self.inputName.setStyleSheet(self.FIELD_STYLE)
        outerLayout.addWidget(self.inputName)

        outerLayout.addWidget(QLabel("CNPJ"))
        self.inputCnpj = QLineEdit(company.get("cnpj", ""))
        self.inputCnpj.setInputMask("00.000.000/0000-00;_")
        self.inputCnpj.setStyleSheet(self.FIELD_STYLE)
        outerLayout.addWidget(self.inputCnpj)

        outerLayout.addWidget(QLabel("Certificado Digital"))
        certRow = QHBoxLayout()
        self.inputCertificate = QLineEdit(company.get("certificate_path", ""))
        self.inputCertificate.setReadOnly(True)
        self.inputCertificate.setStyleSheet(self.FIELD_STYLE)
        btnBrowseCert = QPushButton()
        btnBrowseCert.setObjectName("btnBrowseCert")
        btnBrowseCert.setIcon(QIcon("images/icone-Caminho-semfundo.png"))
        btnBrowseCert.setStyleSheet("""
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
        btnBrowseCert.setCursor(Qt.CursorShape.PointingHandCursor)
        btnBrowseCert.setFixedWidth(32)
        btnBrowseCert.clicked.connect(self._browseCertificate)
        certRow.addWidget(self.inputCertificate)
        certRow.addWidget(btnBrowseCert)
        outerLayout.addLayout(certRow)

        outerLayout.addWidget(QLabel("Serviços cadastrados"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        servicesContainer = QWidget()
        self.servicesLayout = QVBoxLayout(servicesContainer)
        self.servicesLayout.setSpacing(8)
        scroll.setWidget(servicesContainer)
        outerLayout.addWidget(scroll)

        self._buildServiceFields(company)

        buttonsRow = QHBoxLayout()
        btnCancel = QPushButton("Cancelar")
        btnCancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btnCancel.setStyleSheet("""
            background-color: transparent; border: 1px solid #EEEEEE;
            border-radius: 5px; padding: 6px; color: #042e67;
        """)
        btnCancel.clicked.connect(self.reject)

        btnSave = QPushButton("Salvar")
        btnSave.setCursor(Qt.CursorShape.PointingHandCursor)
        btnSave.setStyleSheet("""
            background-color: #06adc2; border-radius: 5px;
            padding: 6px; color: white; font-weight: 700;
        """)
        btnSave.clicked.connect(self._onSaveClicked)

        buttonsRow.addWidget(btnCancel)
        buttonsRow.addWidget(btnSave)
        outerLayout.addLayout(buttonsRow)

    def _buildServiceFields(self, company: dict):
        systemLogins = company.get("system_logins", [])
        registered = [
            login for login in systemLogins
            if login.get("login") and login.get("password") is not None
        ]

        if not registered:
            self.servicesLayout.addWidget(QLabel("Nenhum serviço de NF cadastrado."))
            return

        for login in registered:
            key = login["system_name"]
            displayName = SYSTEM_KEY_TO_DISPLAY_NAME.get(key, key)

            block = QFrame()
            blockLayout = QVBoxLayout(block)
            blockLayout.setContentsMargins(0, 0, 0, 0)
            blockLayout.setSpacing(4)

            blockLayout.addWidget(QLabel(displayName))

            if key in CERTIFICATE_BASED_SYSTEM_KEYS:
                row = QHBoxLayout()
                inputCert = QLineEdit(login.get("login", ""))
                inputCert.setReadOnly(True)
                inputCert.setPlaceholderText("Certificado deste sistema")
                inputCert.setStyleSheet(self.FIELD_STYLE)
                btnBrowse = QPushButton("...")
                btnBrowse.setCursor(Qt.CursorShape.PointingHandCursor)
                btnBrowse.setFixedWidth(32)
                btnBrowse.clicked.connect(lambda _, field=inputCert: self._browseGenericCertificate(field))
                row.addWidget(inputCert)
                row.addWidget(btnBrowse)
                blockLayout.addLayout(row)

                self._serviceFields[key] = {"login": inputCert, "password": None}
            else:
                inputLogin = QLineEdit(login.get("login", ""))
                inputLogin.setPlaceholderText("Login/Usuário")
                inputLogin.setStyleSheet(self.FIELD_STYLE)
                inputPassword = QLineEdit(login.get("password", ""))
                inputPassword.setPlaceholderText("Senha")
                inputPassword.setStyleSheet(self.FIELD_STYLE)

                blockLayout.addWidget(inputLogin)
                blockLayout.addWidget(inputPassword)

                self._serviceFields[key] = {"login": inputLogin, "password": inputPassword}

            self.servicesLayout.addWidget(block)

    def _browseCertificate(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Certificado", "", "Certificado Digital (*.pfx *.p12)"
        )
        if path:
            self.inputCertificate.setText(path)

    def _browseGenericCertificate(self, field: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Certificado", "", "Certificado Digital (*.pfx *.p12)"
        )
        if path:
            field.setText(path)

    def _onSaveClicked(self):
        companyData = {
            "name": self.inputName.text().strip(),
            "cnpj": self.inputCnpj.text(),
            "im": self.company.get("im", ""),
            "certificate_path": self.inputCertificate.text().strip(),
        }

        servicesData = []
        for key, fields in self._serviceFields.items():
            loginValue = fields["login"].text().strip()
            passwordValue = fields["password"].text().strip() if fields["password"] else ""
            servicesData.append({
                "system_name": key,
                "login": loginValue,
                "password": passwordValue,
            })

        self.result_data = {"company": companyData, "services": servicesData}
        self.accept()