from PySide6.QtCore import QThread, Signal
from services.CompanyApiService import CompanyApiService

class AddSystemLoginWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, companyId: int, systemName: str, login: str, password: str):
        super().__init__()
        self.companyId = companyId
        self.systemName = systemName
        self.login = login
        self.password = password

    def run(self):
        try:
            CompanyApiService.addSystemLogin(self.companyId, self.systemName, self.login, self.password)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))