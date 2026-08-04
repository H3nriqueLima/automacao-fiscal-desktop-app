from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget
from PySide6.QtCore import Qt

from models.TaskMappings import SYSTEM_KEY_TO_DISPLAY_NAME, DISPLAY_NAME_TO_NF_TYPE


class RunAutomationDialog(QDialog):

    def __init__(self, taskType: str, taskTitle: str, companies: list[dict],
                 requiresSystem: bool = False, parent: QWidget | None = None):
        super().__init__(parent)

        self.taskType = taskType
        self.companies = companies
        self.requiresSystem = requiresSystem

        self.selectedCompanyId: int | None = None
        self.selectedNfType: str | None = None

        self.setWindowTitle(f"Rodar Automação — {taskTitle}")
        self.setFixedSize(300, 220 if requiresSystem else 180)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #042e67;
                font-weight: 600;
            }
            QComboBox {
                background-color: transparent;
                border: 1px solid #EEEEEE;
                border-radius: 5px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Empresa"))
        self.boxCompany = QComboBox()

        if companies:
            for company in companies:
                self.boxCompany.addItem(company["name"], userData=company["id"])
        else:
            self.boxCompany.addItem("Nenhuma empresa cadastrada")
            self.boxCompany.setEnabled(False)

        layout.addWidget(self.boxCompany)

        self.boxSystem = QComboBox()
        if requiresSystem:
            layout.addWidget(QLabel("Sistema / Site"))
            layout.addWidget(self.boxSystem)
            self.boxCompany.currentIndexChanged.connect(self._refreshSystemOptions)
            self._refreshSystemOptions()

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

        btnRun = QPushButton("Rodar Automação")
        btnRun.setCursor(Qt.CursorShape.PointingHandCursor)
        btnRun.setStyleSheet("""
            background-color: #06adc2;
            border-radius: 5px;
            padding: 6px;
            color: white;
            font-weight: 700;
        """)
        btnRun.clicked.connect(self._onRunClicked)

        buttonsRow.addWidget(btnCancel)
        buttonsRow.addWidget(btnRun)
        layout.addLayout(buttonsRow)

    def _refreshSystemOptions(self):
        companyIndex = self.boxCompany.currentIndex()
        if companyIndex < 0 or companyIndex >= len(self.companies):
            registeredKeys = []
        else:
            company = self.companies[companyIndex]
            systemLogins = company.get("system_logins", [])
            registeredKeys = [
                login["system_name"] for login in systemLogins
                if login.get("login") and login.get("password")
            ]

        registeredNames = [SYSTEM_KEY_TO_DISPLAY_NAME[k] for k in registeredKeys if k in SYSTEM_KEY_TO_DISPLAY_NAME]

        self.boxSystem.blockSignals(True)
        self.boxSystem.clear()

        if registeredNames:
            self.boxSystem.addItems(registeredNames)
            self.boxSystem.setEnabled(True)
        else:
            self.boxSystem.addItem("Nenhum sistema cadastrado para esta empresa")
            self.boxSystem.setEnabled(False)

        self.boxSystem.blockSignals(False)

    def _onRunClicked(self):
        if not self.boxCompany.isEnabled():
            return

        if self.requiresSystem and not self.boxSystem.isEnabled():
            return

        self.selectedCompanyId = self.boxCompany.currentData()

        if self.requiresSystem:
            systemText = self.boxSystem.currentText()
            self.selectedNfType = DISPLAY_NAME_TO_NF_TYPE.get(systemText)
            if self.selectedNfType is None:
                return

        self.accept()