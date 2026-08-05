from PySide6.QtCore import QThread, Signal
from services.CompanyApiService import CompanyApiService


class UpdateCompanyFullWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, companyId: int, companyData: dict, servicesData: list[dict]):
        super().__init__()
        self.companyId = companyId
        self.companyData = companyData
        self.servicesData = servicesData

    def run(self):
        try:
            CompanyApiService.updateCompany(
                self.companyId,
                self.companyData["name"],
                self.companyData["cnpj"],
                self.companyData["im"],
                self.companyData["certificate_path"]
            )

            for service in self.servicesData:
                CompanyApiService.addSystemLogin(
                    self.companyId,
                    service["system_name"],
                    service["login"],
                    service["password"]
                )

            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))