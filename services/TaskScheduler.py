from PySide6.QtCore import QDate, QTime, QTimer, QObject, Signal

from automation.AutomationDispatcher import AutomationDispatcher
from workers.AutomationExecutionWorker import AutomationExecutionWorker
from workers.CheckDueTasksWorker import CheckDueTasksWorker


class TaskScheduler(QObject):
    taskExecuted = Signal(dict, bool, str)

    def __init__(self, checkIntervalMs: int = 60_000, parent=None):
        super().__init__(parent)
        self.dispatcher = AutomationDispatcher()
        self._executedToday: set[int] = set()
        self._activeWorkers: list[AutomationExecutionWorker] = []
        self._lastResetDate = QDate.currentDate()
        self._checkWorker: CheckDueTasksWorker | None = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._checkDueTasks)
        self.timer.setInterval(checkIntervalMs)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def _checkDueTasks(self):
        self._resetIfNewDay()

        if self._checkWorker is not None and self._checkWorker.isRunning():
            return

        self._checkWorker = CheckDueTasksWorker()
        self._checkWorker.finished.connect(self._onCompaniesFetched)
        self._checkWorker.start()

    def _onCompaniesFetched(self, success: bool, companies: list):
        if not success:
            return

        today = QDate.currentDate().toString("dd/MM/yyyy")
        currentHour = QTime.currentTime().toString("HH:mm")

        for company in companies:
            for task in company.get("tasks", []):
                if self._isDue(task, today, currentHour):
                    self._startExecution(company, task)

    def _resetIfNewDay(self):
        today = QDate.currentDate()
        if today != self._lastResetDate:
            self._executedToday.clear()
            self._lastResetDate = today

    def _isDue(self, task: dict, today: str, currentHour: str) -> bool:
        taskId = task.get("id")
        if taskId in self._executedToday:
            return False
        return task.get("date") == today and task.get("hour") == currentHour

    def _startExecution(self, company: dict, task: dict):
        self._executedToday.add(task["id"])

        worker = AutomationExecutionWorker(self.dispatcher, company, task)
        worker.finished.connect(self._onWorkerFinished)
        self._activeWorkers.append(worker)
        worker.start()

    def _onWorkerFinished(self, taskData: dict, success: bool, message: str):
        self._activeWorkers = [w for w in self._activeWorkers if w.isRunning()]
        self.taskExecuted.emit(taskData, success, message)