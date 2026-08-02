from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QWidget


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

    # GETTERS
    def getSystemName(self) -> str:
        return self.systemName

    def getLogin(self) -> str:
        return self.loginField.text()

    def getPassword(self) -> str:
        return self.passwordField.text()