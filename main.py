import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QDialog
from PySide6.QtCore import Qt, QDate, QTimer
from typing import cast

from custom_widgets.ListWidgetCheck import ListWidgetCheck
from custom_widgets.TaskEditDialog import TaskEditDialog
from models.TaskMappings import BOX_SCHEDULE_TO_TASK_TYPE, SYSTEM_KEY_TO_DISPLAY_NAME, \
    DISPLAY_NAME_TO_NF_TYPE
from services.FeatureButtons import FeatureButtons
from services.RegisterCompany import RegisterCompany
from services.SelectCertificate import SelectCertificate
from services.ValidateDataRegister import DataValidator
from services.Navigator import Navigator
from workers.CreateTaskWorker import CreateTaskWorker
from workers.DeleteTaskWorker import DeleteTaskWorker
from workers.LoadCompaniesWorker import LoadCompaniesWorker
from workers.LoadTasksWorker import LoadTasksWorker
from workers.RegisterCompanyWorker import RegisterCompanyWorker
from utils.resourcePath import resourcePath
from utils.updateDayWeekHour import updateDayWeekHour
from workers.UpdateTaskWorker import UpdateTaskWorker

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from mainWindow_ui import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # workers (guardados como atributo para não serem coletados pelo garbage collector)
        self.registerWorker = None
        self.loadCompaniesWorker = None
        self.createTaskWorker = None
        self.loadTasksWorker = None
        self.updateTaskWorker = None
        self.deleteTaskWorker = None
        self.loadedCompanies: list[dict] = []

        self._setupScrollLayouts()
        self._setupClock()
        self._setupNavigation()
        self._setupSystemsList()
        self._setupScheduleTypeOptions()
        self._setupCompanyRegistration()
        self._setupScheduling()

        self._currentTasksCache: list[dict] = []

        self.goToHome()

    # ------------------------------------------------------------------
    # SETUP — cada mét0do monta uma parte isolada da tela
    # ------------------------------------------------------------------

    def _setupScrollLayouts(self):
        self.scrollLayoutTasks = cast(QVBoxLayout, self.ui.scrollAreaWidgetContents.layout())
        self.scrollLayoutSystems = cast(QVBoxLayout, self.ui.scrollAreaWidgetContentsLogins.layout())
        self.scrollLayoutTasks.addStretch()
        self.scrollLayoutSystems.addStretch()

        self.featureButtons = FeatureButtons()

    def _setupClock(self):
        self.ui.dateIcon.setImage(resourcePath("images/icone-Data-semfundo.png"))
        self.ui.trueDate.setText(QDate.currentDate().toString("dd/MM/yyyy"))

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.ui.dateWeekHour.setText(updateDayWeekHour()))
        self.timer.start(1000)
        self.ui.dateWeekHour.setText(updateDayWeekHour())

    def _setupNavigation(self):
        self.navigator = Navigator(self.ui.stackedWidget)

        self.ui.registerCompany.clicked.connect(self.goToRegisterCompany)
        self.ui.taskScheduling.clicked.connect(self.onOpenScheduling)
        self.ui.configurations.clicked.connect(self.goToConfig)
        self.ui.homeButtonConfig.clicked.connect(self.goToHome)
        self.ui.homeButtonConfigSched.clicked.connect(self.goToHome)
        self.ui.homeButtonRegisterCompany.clicked.connect(self.goToHome)

        # transparência de clique nos títulos, para não impedir o clique dos botões de tarefas
        self.ui.buttonTitleDAS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleEFDCont.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleICMS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleNotas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setupSystemsList(self):
        contentSystems = self.ui.selectSystemsContent
        layoutSystems = QVBoxLayout()
        layoutSystems.setContentsMargins(0, 9, 0, 9)
        contentSystems.setLayout(layoutSystems)

        self.systemsList = ListWidgetCheck(["Nota do Milhão", "IOB", "Memocash", "GINFES", "GISS Nova"])
        layoutSystems.addWidget(self.systemsList)

        self.systemsList.itemClicked.connect(lambda: self.featureButtons.onSystemToggled(
            self.systemsList.currentItem(),
            self.scrollLayoutSystems,
            "",
            ""
        ))

    def _setupScheduleTypeOptions(self):
        self.ui.boxSchedule.clear()
        self.ui.boxSchedule.addItems([
            "DAS (PGDAS-D e-CAC)",
            "EFD ICMS/IPI",
            "EFD Contribuições",
            "Consulta de Notas Fiscais"
        ])

        self.ui.boxNfType.clear()
        self.ui.boxNfType.setEnabled(False)

        self.ui.boxSchedule.currentTextChanged.connect(self.onScheduleTypeChanged)

    def _setupCompanyRegistration(self):
        self.companyValidator = DataValidator(self.ui)
        self.registerCompany = RegisterCompany(self.ui)
        self.selectCertificate = SelectCertificate(self.ui)

        self.ui.buttonSearchPathCertificate.clicked.connect(self.selectCertificate.selectFile)
        self.ui.buttonCancelCompany.clicked.connect(self.cancelCompany)
        self.ui.buttonSaveCompany.clicked.connect(self.onRegisterCompanyClicked)

    def _setupScheduling(self):
        self.ui.boxCompanyScheduling.currentIndexChanged.connect(self.onCompanySelected)
        self.ui.createButtonSchedule.clicked.connect(self.onCreateTaskClicked)
        self.ui.cancelButtonSchedule.clicked.connect(self.cancelScheduling)
        self.ui.updateListSched.clicked.connect(self.reloadTasksForSelectedCompany)

        self.ui.startScheduleDate.setMinimumDate(QDate.currentDate())

        # ------------------------------------------------------------------
    # NAVEGAÇÃO
    # ------------------------------------------------------------------

    def goToRegisterCompany(self):
        self.navigator.openPage(self.ui.pageRegisterCompany)

    def goToScheduling(self):
        self.navigator.openPage(self.ui.pageScheduling)

    def goToConfig(self):
        self.navigator.openPage(self.ui.pageConfigurations)

    def goToHome(self):
        self.navigator.openPage(self.ui.pageHome)

    # ------------------------------------------------------------------
    # CADASTRO DE EMPRESA
    # ------------------------------------------------------------------

    def onRegisterCompanyClicked(self):
        missingData = self.companyValidator.validateRegisterCompanyData()
        if missingData:
            self.companyValidator.showWarningIncompleteData(missingData)
            return

        company = self.registerCompany.register()

        self.ui.buttonSaveCompany.setEnabled(False)
        self.ui.buttonSaveCompany.setText("Salvando...")

        self.registerWorker = RegisterCompanyWorker(self.registerCompany, company)
        self.registerWorker.finished.connect(self.onRegisterFinished)
        self.registerWorker.start()

    def onRegisterFinished(self, success: bool, errorMessage: str):
        self.ui.buttonSaveCompany.setEnabled(True)
        self.ui.buttonSaveCompany.setText("Salvar Empresa")

        if success:
            QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
            self.goToHome()
        else:
            QMessageBox.critical(self, "Erro", f"Não foi possível cadastrar a empresa.\n\n{errorMessage}")

    def cancelCompany(self):
        self.ui.companyName.clear()
        self.ui.cnpjNumber.clear()
        self.ui.imNumber.clear()
        self.ui.pathCertificate.clear()

        for i in range(self.systemsList.count()):
            item = self.systemsList.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.featureButtons.clearSystems(self.scrollLayoutSystems)

    # ------------------------------------------------------------------
    # AGENDAMENTO DE TAREFAS
    # ------------------------------------------------------------------

    def onOpenScheduling(self):
        self.goToScheduling()
        if self.loadCompaniesWorker is None or not self.loadCompaniesWorker.isRunning():
            self.loadCompanies()

    def loadCompanies(self):
        self.ui.boxCompanyScheduling.setEnabled(False)
        self.loadCompaniesWorker = LoadCompaniesWorker()
        self.loadCompaniesWorker.finished.connect(self.onCompaniesLoaded)
        self.loadCompaniesWorker.start()

    def onCompaniesLoaded(self, success: bool, companies: list, errorMessage: str):
        self.ui.boxCompanyScheduling.setEnabled(True)

        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar as empresas.\n\n{errorMessage}")
            return

        self.loadedCompanies = companies

        self.ui.boxCompanyScheduling.blockSignals(True)
        self.ui.boxCompanyScheduling.clear()

        for company in companies:
            self.ui.boxCompanyScheduling.addItem(company["name"], userData=company["id"])

        self.ui.boxCompanyScheduling.blockSignals(False)

        if companies:
            self.onCompanySelected(0)

    def onCompanySelected(self, index: int):
        if index < 0 or index >= len(self.loadedCompanies):
            return
        self._refreshNfTypeOptions()
        self.reloadTasksForSelectedCompany()

    def reloadTasksForSelectedCompany(self):
        companyId = self.ui.boxCompanyScheduling.currentData()
        if companyId is None:
            return

        if self.loadTasksWorker is not None and self.loadTasksWorker.isRunning():
            return

        self.ui.updateListSched.setEnabled(False)
        self.ui.boxCompanyScheduling.setEnabled(False)

        self.loadTasksWorker = LoadTasksWorker(companyId)
        self.loadTasksWorker.finished.connect(self.onTasksLoaded)
        self.loadTasksWorker.start()

    def onTasksLoaded(self, success: bool, tasks: list, errorMessage: str):
        self.ui.updateListSched.setEnabled(True)
        self.ui.boxCompanyScheduling.setEnabled(True)

        self._currentTasksCache = tasks

        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar as tarefas.\n\n{errorMessage}")
            return

        self.featureButtons.clearTasks(self.scrollLayoutTasks)

        for taskData in tasks:
            title, iconPath = self.featureButtons.getTaskDisplayInfo(taskData)
            self.featureButtons.addTaskFromApi(
                taskData, title, iconPath, self.scrollLayoutTasks,
                onEdit=self.onEditTaskRequested,
                onDelete=self.onDeleteTaskRequested
            )

        self.ui.totalSchedulings.setText(f"Total de Agendamentos: {len(tasks)}")

    def onCreateTaskClicked(self):
        companyId = self.ui.boxCompanyScheduling.currentData()
        if companyId is None:
            QMessageBox.warning(self, "Atenção", "Selecione uma empresa antes de criar o agendamento.")
            return

        if self.ui.startScheduleDate.date() < QDate.currentDate():
            QMessageBox.warning(self, "Atenção", "A data de início não pode ser anterior a hoje.")
            return

        scheduleText = self.ui.boxSchedule.currentText()
        taskType = BOX_SCHEDULE_TO_TASK_TYPE.get(scheduleText, "DAS")

        nfType = None
        if taskType == "NF":
            registeredKeys = self._getRegisteredSystemsForCurrentCompany()
            if not registeredKeys:
                QMessageBox.warning(self, "Atenção",
                                    "Esta empresa não possui nenhum sistema de notas fiscais cadastrado.")
                return

            systemText = self.ui.boxNfType.currentText()
            nfType = DISPLAY_NAME_TO_NF_TYPE.get(systemText)

            if nfType is None:
                QMessageBox.warning(self, "Atenção", "Selecione um sistema de Notas Fiscais válido.")
                return

        taskData = {
            "task_type": taskType,
            "freq_type": f"A cada {self.ui.boxRepeatQntDays.value()} {self.ui.boxRepeatQtnDaysType.currentText()}",
            "freq_info": f"Todo dia {self.ui.startScheduleDate.date().day()}",
            "date": self.ui.startScheduleDate.date().toString("dd/MM/yyyy"),
            "hour": self.ui.hourSchedule.time().toString("HH:mm"),
            "nf_type": nfType,
        }

        self.ui.createButtonSchedule.setEnabled(False)
        self.ui.createButtonSchedule.setText("Criando...")

        self.createTaskWorker = CreateTaskWorker(companyId, taskData)
        self.createTaskWorker.finished.connect(self.onTaskCreated)
        self.createTaskWorker.start()

    def onTaskCreated(self, success: bool, task: dict, errorMessage: str):
        self.ui.createButtonSchedule.setEnabled(True)
        self.ui.createButtonSchedule.setText("Criar Agendamento")

        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível criar o agendamento.\n\n{errorMessage}")
            return

        QMessageBox.information(self, "Sucesso", "Agendamento criado com sucesso!")
        self.cancelScheduling()
        self.reloadTasksForSelectedCompany()

    def cancelScheduling(self):
        self.ui.boxSchedule.setCurrentIndex(0)
        self.ui.boxNfType.setCurrentIndex(0)
        self.ui.boxNfType.setEnabled(False)

        self.ui.startScheduleDate.setDate(QDate.currentDate())
        self.ui.hourSchedule.setTime(self.ui.hourSchedule.minimumTime())

        self.ui.boxTypeRepeat.setCurrentIndex(0)
        self.ui.boxRepeatQntDays.setValue(0)
        self.ui.boxRepeatQtnDaysType.setCurrentIndex(0)

    def onScheduleTypeChanged(self, text: str):
        self._refreshNfTypeOptions()

    def _getRegisteredSystemsForCurrentCompany(self) -> list[str]:
        companyId = self.ui.boxCompanyScheduling.currentData()
        if companyId is None:
            return []

        company = next((c for c in self.loadedCompanies if c["id"] == companyId), None)
        if company is None:
            return []

        systemLogins = company.get("system_logins", [])

        return [
            login["system_name"] for login in systemLogins
            if login.get("login") and login.get("password")
        ]

    def _refreshNfTypeOptions(self):
        registeredKeys = self._getRegisteredSystemsForCurrentCompany()
        registeredNames = [
            SYSTEM_KEY_TO_DISPLAY_NAME[key] for key in registeredKeys
            if key in SYSTEM_KEY_TO_DISPLAY_NAME
        ]

        self.ui.boxNfType.blockSignals(True)
        self.ui.boxNfType.clear()

        if registeredNames:
            self.ui.boxNfType.addItems(registeredNames)
            self.ui.boxNfType.setEnabled(self.ui.boxSchedule.currentText() == "Consulta de Notas Fiscais")
        else:
            self.ui.boxNfType.addItem("Nenhum sistema de notas cadastrado para esta empresa")
            self.ui.boxNfType.setEnabled(False)

        self.ui.boxNfType.blockSignals(False)

    def onEditTaskRequested(self, taskId: int):
        if self.updateTaskWorker is not None and self.updateTaskWorker.isRunning():
            return

        taskData = next((t for t in self._currentTasksCache if t["id"] == taskId), None)
        if taskData is None:
            return

        registeredKeys = self._getRegisteredSystemsForCurrentCompany()
        dialog = TaskEditDialog(taskData, registeredKeys, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_data:
            companyId = self.ui.boxCompanyScheduling.currentData()
            self.updateTaskWorker = UpdateTaskWorker(companyId, taskId, dialog.result_data)
            self.updateTaskWorker.finished.connect(self.onTaskUpdated)
            self.updateTaskWorker.start()

    def onTaskUpdated(self, success: bool, errorMessage: str):
        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível atualizar a tarefa.\n\n{errorMessage}")
            return

        QMessageBox.information(self, "Sucesso", "Tarefa atualizada com sucesso!")
        self.reloadTasksForSelectedCompany()

    def onDeleteTaskRequested(self, taskId: int):
        if self.deleteTaskWorker is not None and self.deleteTaskWorker.isRunning():
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão", "Tem certeza que deseja excluir esta tarefa?"
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        companyId = self.ui.boxCompanyScheduling.currentData()
        self.deleteTaskWorker = DeleteTaskWorker(companyId, taskId)
        self.deleteTaskWorker.finished.connect(self.onTaskDeleted)
        self.deleteTaskWorker.start()

    def onTaskDeleted(self, success: bool, errorMessage: str):
        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível excluir a tarefa.\n\n{errorMessage}")
            return

        self.reloadTasksForSelectedCompany()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())