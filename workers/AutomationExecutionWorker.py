from PySide6.QtCore import QThread, Signal
from automation.AutomationDispatcher import AutomationDispatcher


class AutomationExecutionWorker(QThread):
    finished = Signal(dict, bool, str)

    def __init__(self, dispatcher: AutomationDispatcher, company: dict, task: dict):
        super().__init__()
        self.dispatcher = dispatcher
        self.company = company
        self.task = task

    def run(self):
        taskType = self.task.get("task_type", "")
        try:
            result = self.dispatcher.dispatch(taskType, self.company, self.task)
            self.finished.emit(self.task, result.success, result.message)
        except Exception as e:
            self.finished.emit(self.task, False, str(e))