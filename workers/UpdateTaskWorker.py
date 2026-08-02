from PySide6.QtCore import QThread, Signal
from services.CompanyApiService import CompanyApiService

class UpdateTaskWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, companyId: int, taskId: int, taskData: dict):
        super().__init__()
        self.companyId = companyId
        self.taskId = taskId
        self.taskData = taskData

    def run(self):
        try:
            CompanyApiService.updateTask(self.companyId, self.taskId, self.taskData)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))