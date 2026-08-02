from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QLineEdit, QWidget
from PySide6.QtCore import Qt

from utils.resourcePath import resourcePath


class SystemRowWidget(QFrame):

    def __init__(self,
                 systemName:str,
                 login:str,
                 password:str,
                 parent:QWidget|None=None):
        super().__init__(parent)

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

        # Layout da linha
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Titulo do Sistema
        systemNameColumn = QFrame()
        layoutSystemNameColumn = QHBoxLayout(systemNameColumn)
        systemNameLabel = QLabel(systemName)

        systemNameLabel.setStyleSheet("color: #182946; font-weight: 700;")
        systemNameColumn.setFixedWidth(190)
        layoutSystemNameColumn.setContentsMargins(0,0,0,0)
        layoutSystemNameColumn.setSpacing(0)
        layoutSystemNameColumn.addWidget(systemNameLabel)
        layout.addWidget(systemNameColumn)

        # Login do Sistema
        loginColumn = QFrame()
        layoutLoginColumn = QVBoxLayout(loginColumn)
        loginLine = QLineEdit(login)

        loginLine.setStyleSheet("background-color: white; border: 1px solid lightgray; border-radius: 5px; padding: 4px;")
        loginLine.setPlaceholderText("Login/Usuário")

        loginColumn.setFixedWidth(210)
        layoutLoginColumn.setContentsMargins(9,6,9,6)
        layoutLoginColumn.setSpacing(0)
        layoutLoginColumn.addWidget(loginLine)
        layout.addWidget(loginColumn)

        # Data/Hora (Repetição)
        passwordColumn = QFrame()
        layoutPasswordColumn = QVBoxLayout(passwordColumn)
        passwordLine = QLineEdit(password)

        passwordLine.setStyleSheet("background-color: white; border: 1px solid lightgray; border-radius: 5px; padding: 4px;")

        passwordColumn.setFixedWidth(210)
        layoutPasswordColumn.setContentsMargins(9,6,9,6)
        layoutPasswordColumn.setSpacing(0)
        layoutPasswordColumn.addWidget(passwordLine)
        layout.addWidget(passwordColumn)

        # guardar os dados para os GETTERS
        self.systemName:str = systemName
        self.loginField = loginLine
        self.passwordField = passwordLine

        # # Botões de ação (editar/excluir)
        # systemButtonsColumn = QFrame()
        # layoutSystemButtonsColumn = QHBoxLayout(systemButtonsColumn)
        # systemEdit = QPushButton()
        # systemDelete = QPushButton()
        #
        # systemEdit.setObjectName("SystemEdit")
        # systemEdit.setIcon(QIcon(resourcePath("images/icone-Editar-semfundo.png")))
        # systemEdit.setCursor(Qt.CursorShape.PointingHandCursor)
        # systemEdit.setStyleSheet("""
        #     #SystemEdit {
        #         background-color: white;
        #         border: 1px solid lightgray;
        #         border-radius: 5px;
        #         width: 30px;
        #         height: 30px;
        #     }
        #     #SystemEdit:hover {
        #         background-color: lightgray;
        #     }
        # """)
        #
        # systemDelete.setObjectName("SystemDelete")
        # systemDelete.setIcon(QIcon(resourcePath("images/icone-Excluir-semfundo.png")))
        # systemDelete.setCursor(Qt.CursorShape.PointingHandCursor)
        # systemDelete.setStyleSheet("""
        #     #SystemDelete {
        #         background-color: white;
        #         border: 1px solid lightgray;
        #         border-radius: 5px;
        #         width: 30px;
        #         height: 30px;
        #     }
        #     #SystemDelete:hover {
        #         background-color: lightgray;
        #     }
        # """)
        #
        # systemButtonsColumn.setFixedWidth(80)
        # layoutSystemButtonsColumn.setContentsMargins(9,0,0,0)
        # layoutSystemButtonsColumn.setSpacing(6)
        # layoutSystemButtonsColumn.addWidget(systemEdit)
        # layoutSystemButtonsColumn.addWidget(systemDelete)
        # layout.addWidget(systemButtonsColumn)

    # GETTERS
    def getSystemName(self) -> str:
        return self.systemName

    def getLogin(self) -> str:
        return self.loginField.text()

    def getPassword(self) -> str:
        return self.passwordField.text()