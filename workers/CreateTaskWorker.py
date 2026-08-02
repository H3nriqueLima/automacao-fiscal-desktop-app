from PySide6.QtCore import QThread, Signal

from services.CompanyApiService import CompanyApiService

class CreateTaskWorker(QThread):
    finished = Signal(bool, dict, str)  # sucesso, task criada, erro

    def __init__(self, companyId: int, taskData: dict):
        super().__init__()
        self.companyId = companyId
        self.taskData = taskData

    def run(self):
        try:
            task = CompanyApiService.createTask(self.companyId, self.taskData)
            self.finished.emit(True, task, "")
        except Exception as error:
            self.finished.emit(False, {}, str(error))