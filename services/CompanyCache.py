from PySide6.QtCore import QObject, Signal
from workers.LoadCompaniesWorker import LoadCompaniesWorker


class CompanyCache(QObject):

    dataUpdated = Signal(list)
    loadFailed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._companies: list[dict] = []
        self._worker: LoadCompaniesWorker | None = None
        self._isLoaded = False

    def isLoaded(self) -> bool:
        return self._isLoaded

    def getAll(self) -> list[dict]:
        return self._companies

    def getById(self, companyId: int) -> dict | None:
        return next((c for c in self._companies if c["id"] == companyId), None)

    def getRegisteredSystemKeys(self, companyId: int) -> list[str]:
        company = self.getById(companyId)
        if company is None:
            return []
        return [
            login["system_name"] for login in company.get("system_logins", [])
            if login.get("login") and login.get("password")
        ]

    def refresh(self):
        if self._worker is not None and self._worker.isRunning():
            return

        self._worker = LoadCompaniesWorker()
        self._worker.finished.connect(self._onLoaded)
        self._worker.start()

    def _onLoaded(self, success: bool, companies: list, errorMessage: str):
        if not success:
            self.loadFailed.emit(errorMessage)
            return

        self._companies = companies
        self._isLoaded = True
        self.dataUpdated.emit(self._companies)