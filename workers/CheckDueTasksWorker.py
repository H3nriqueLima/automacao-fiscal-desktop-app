from PySide6.QtCore import QThread, Signal
from services.CompanyApiService import CompanyApiService


class CheckDueTasksWorker(QThread):
    finished = Signal(bool, list)

    def run(self):
        try:
            companies = CompanyApiService.listCompanies()
            self.finished.emit(True, companies)
        except Exception:
            self.finished.emit(False, [])