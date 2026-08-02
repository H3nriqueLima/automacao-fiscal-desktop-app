from PySide6.QtCore import QThread, Signal

from services.RegisterCompany import RegisterCompany

class RegisterCompanyWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, registerCompanyService: RegisterCompany, company, /):
        super().__init__()
        self.registerCompanyService = registerCompanyService
        self.company = company

    def run(self):
        try:
            success = self.registerCompanyService.sendToApi(self.company)
            if success:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "Não foi possível cadastrar a empresa.")
        except Exception as error:
            self.finished.emit(False, str(error))