from abc import ABC, abstractmethod


class AutomationResult:

    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message


class AutomationTask(ABC):
    # Contrato que todas as rotinas de automação vai seguir

    @abstractmethod
    def run(self, companyData: dict, taskData: dict) -> AutomationResult:
        print("")