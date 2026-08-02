from PySide6.QtCore import QThread, Signal
from services.CompanyApiService import CompanyApiService

class DeleteTaskWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, companyId: int, taskId: int):
        super().__init__()
        self.companyId = companyId
        self.taskId = taskId

    def run(self):
        try:
            CompanyApiService.deleteTask(self.companyId, self.taskId)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))