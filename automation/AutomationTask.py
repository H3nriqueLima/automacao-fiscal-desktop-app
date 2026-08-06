from abc import ABC, abstractmethod

from automation.AutomationContext import AutomationContext


class AutomationResult:

    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message


class AutomationTask(ABC):

    @abstractmethod
    def run(self, companyData: dict, taskData: dict, context: AutomationContext) -> AutomationResult:
        ...