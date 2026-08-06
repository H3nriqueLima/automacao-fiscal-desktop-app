from PySide6.QtCore import QObject, Signal


class AutomationMonitor(QObject):
    taskListChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: dict[int, dict] = {}
        self._nextId = 1

    def register(self, label: str, worker) -> int:
        entryId = self._nextId
        self._nextId += 1
        self._entries[entryId] = {"label": label, "status": "Em andamento", "worker": worker}
        self.taskListChanged.emit()
        return entryId

    def markFinished(self, entryId: int, success: bool):
        if entryId in self._entries:
            self._entries[entryId]["status"] = "Concluído" if success else "Falhou"
            self.taskListChanged.emit()

    def remove(self, entryId: int):
        if entryId in self._entries:
            del self._entries[entryId]
            self.taskListChanged.emit()

    def getAll(self) -> list[dict]:
        return [{"id": k, **v} for k, v in self._entries.items()]

    def stop(self, entryId: int):
        entry = self._entries.get(entryId)
        if entry:
            entry["worker"].requestStop()
            self._entries[entryId]["status"] = "Parando..."
            self.taskListChanged.emit()