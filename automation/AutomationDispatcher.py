from automation.AutomationContext import AutomationContext
from automation.AutomationTask import AutomationResult, AutomationTask


class AutomationDispatcher:

    def __init__(self):
        self._registry: dict[str, AutomationTask] = {}

    def register(self, taskType: str, task):
        self._registry[taskType] = task

    def dispatch(self, taskType: str, companyData: dict, taskData: dict, context: AutomationContext) -> AutomationResult:
        routine = self._registry.get(taskType)

        if routine is None:
            return AutomationResult(success=False, message=f"Nenhuma rotina de automação implementada para '{taskType}' ainda.")

        return routine.run(companyData, taskData, context)