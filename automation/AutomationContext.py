import threading


class AutomationCancelledError(Exception):
    pass

class AutomationContext:

    def __init__(self, cancelEvent: threading.Event, onProgress=None):
        self.cancelEvent = cancelEvent
        self._onProgress = onProgress

    def isCancelled(self) -> bool:
        return self.cancelEvent.is_set()

    def checkCancelled(self):
        if self.isCancelled():
            raise AutomationCancelledError()

    def reportProgress(self, message: str):
        if self._onProgress:
            self._onProgress(message)