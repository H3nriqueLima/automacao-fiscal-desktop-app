import threading

from PySide6.QtCore import QThread, Signal

from automation.AutomationContext import AutomationContext, AutomationCancelledError
from automation.AutomationDispatcher import AutomationDispatcher


class AutomationExecutionWorker(QThread):
    finished = Signal(dict, bool, str)
    progress = Signal(dict, str)

    def __init__(self, dispatcher: AutomationDispatcher, company: dict, task: dict):
        super().__init__()
        self.dispatcher = dispatcher
        self.company = company
        self.task = task
        self._cancelEvent = threading.Event()

    def requestStop(self):
        self._cancelEvent.set()

    def run(self):
        taskType = self.task.get("task_type", "")
        context = AutomationContext(self._cancelEvent, onProgress=self._emitProgress)

        try:
            result = self.dispatcher.dispatch(taskType, self.company, self.task, context)
            self.finished.emit(self.task, result.success, result.message)
        except AutomationCancelledError:
            self.finished.emit(self.task, False, "Automação cancelada pelo usuário.")
        except Exception as e:
            self.finished.emit(self.task, False, str(e))

    def _emitProgress(self, message:str):
        self.progress.emit(self.task, message)