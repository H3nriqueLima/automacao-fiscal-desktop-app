from PySide6.QtCore import QThread, Signal

from services.CompanyApiService import CompanyApiService

class LoadCompaniesWorker(QThread):
    finished = Signal(bool, list, str)

    def run(self):
        try:
            companies = CompanyApiService.listCompanies()
            self.finished.emit(True, companies, "")
        except Exception as error:
            self.finished.emit(False, [], str(error))