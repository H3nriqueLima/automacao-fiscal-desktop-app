from PySide6.QtCore import QThread, Signal

from services.CompanyApiService import CompanyApiService

class LoadTasksWorker(QThread):
    finished = Signal(bool, list, str)

    def __init__(self, companyId: int):
        super().__init__()
        self.companyId = companyId

    def run(self):
        try:
            tasks = CompanyApiService.listTasks(self.companyId)
            self.finished.emit(True, tasks, "")
        except Exception as error:
            self.finished.emit(False, [], str(error))