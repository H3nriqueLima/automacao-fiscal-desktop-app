from PySide6.QtWidgets import QBoxLayout, QListWidgetItem
from PySide6.QtCore import Qt

from custom_widgets.SystemRowWidget import SystemRowWidget
from custom_widgets.TaskRowWidget import TaskRowWidget
from models.TaskMappings import TASK_TYPE_DISPLAY, NF_TYPE_DISPLAY


class FeatureButtons:

    def __init__(self):
        self.systemRows = {}
        self.taskRows = []

    def addTaskFromApi(self, taskData: dict, title: str, iconPath: str, parent: QBoxLayout, onEdit=None, onDelete=None) -> None:
        row = TaskRowWidget(
            taskId=taskData["id"],
            title=title,
            freqType=taskData.get("freq_type", ""),
            freqInfo=taskData.get("freq_info", ""),
            date=taskData.get("date", ""),
            hour=taskData.get("hour", ""),
            iconPath=iconPath
        )

        if onEdit:
            row.editRequested.connect(onEdit)
        if onDelete:
            row.deleteRequested.connect(onDelete)

        parent.insertWidget(parent.count() - 1, row)
        self.taskRows.append(row)

    def onSystemToggled(self,
                        systemListItem: QListWidgetItem,
                        parent: QBoxLayout,
                        systemLogin: str,
                        systemPass: str) -> None:
        itemName: str = systemListItem.text()

        if systemListItem.checkState() == Qt.CheckState.Checked:
            self.__addSystem(itemName, systemLogin, systemPass, parent)
        else:
            self.__removeSystem(itemName, parent)

    def clearSystems(self, parent: QBoxLayout):
        for systemName in list(self.systemRows.keys()):
            self.__removeSystem(systemName, parent)

    def clearTasks(self, parent) -> None:
        for row in self.taskRows:
            parent.removeWidget(row)
            row.deleteLater()
        self.taskRows.clear()

    @staticmethod
    def getTaskDisplayInfo(taskData: dict) -> tuple[str, str]:
        taskType = taskData.get("task_type", "")

        if taskType == "NF":
            nfType = taskData.get("nf_type", "")
            title = NF_TYPE_DISPLAY.get(nfType, "Consulta de Notas Fiscais (Indefinido)")
            iconPath = "images/icone-ConsultaNF-semfundo.png"
            return title, iconPath

        title, iconPath = TASK_TYPE_DISPLAY.get(taskType, ("Tarefa Indefinida", "images/icone-DAS-semfundo.png"))
        return title, iconPath

    def __addSystem(self,
                  systemName: str,
                  systemLogin: str,
                  systemPass: str,
                  parent: QBoxLayout):
        if systemName in self.systemRows:
            return

        system: SystemRowWidget = SystemRowWidget(
            systemName=systemName,
            login=systemLogin,
            password=systemPass
        )

        parent.insertWidget(parent.count() - 1, system)
        self.systemRows[systemName] = system

    def __removeSystem(self, systemName: str, parent: QBoxLayout):
        system: SystemRowWidget | None = self.systemRows.pop(systemName, None)

        if system is not None:
            parent.removeWidget(system)
            system.deleteLater()