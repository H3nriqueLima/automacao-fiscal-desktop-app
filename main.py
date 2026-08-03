import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QDialog, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QDate, QTimer
from typing import cast

from custom_widgets.AddServiceDialog import AddServiceDialog
from custom_widgets.ListWidgetCheck import ListWidgetCheck
from custom_widgets.TaskEditDialog import TaskEditDialog
from models.TaskMappings import BOX_SCHEDULE_TO_TASK_TYPE, SYSTEM_KEY_TO_DISPLAY_NAME, DISPLAY_NAME_TO_NF_TYPE, CONFIG_SERVICE_OPTIONS, ADD_SERVICE_OPTION_TEXT
from services.FeatureButtons import FeatureButtons
from services.RegisterCompany import RegisterCompany
from services.SelectCertificate import SelectCertificate
from services.TaskScheduler import TaskScheduler
from services.ValidateDataRegister import DataValidator
from services.Navigator import Navigator
from workers.AddSystemLoginWorker import AddSystemLoginWorker
from workers.CreateTaskWorker import CreateTaskWorker
from workers.DeleteTaskWorker import DeleteTaskWorker
from workers.LoadCompaniesWorker import LoadCompaniesWorker
from workers.LoadTasksWorker import LoadTasksWorker
from workers.RegisterCompanyWorker import RegisterCompanyWorker
from workers.UpdateTaskWorker import UpdateTaskWorker
from utils.resourcePath import resourcePath
from utils.updateDayWeekHour import updateDayWeekHour

# ajusta o diretório de trabalho para funcionar tanto rodando via python quanto empacotado (.exe)
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

        # workers guardados como atributo para não serem coletados pelo garbage collector, enquanto continuam a rodar em segundo plano
        self.registerWorker = None
        self.loadCompaniesWorker = None
        self.createTaskWorker = None
        self.loadTasksWorker = None
        self.updateTaskWorker = None
        self.deleteTaskWorker = None
        self.addSystemLoginWorker = None
        self.loadCompaniesConfigWorker = None

        # cache dos dados vindos da API, evita ficar a buscar de novo toda hora
        self.loadedCompanies: list[dict] = []
        self.loadedCompaniesConfig: list[dict] = []
        self._currentTasksCache: list[dict] = []

        self._setupScrollLayouts()
        self._setupClock()
        self._setupNavigation()
        self._setupSystemsList()
        self._setupScheduleTypeOptions()
        self._setupCompanyRegistration()
        self._setupScheduling()
        self._setupSystemTray()

        self.goToHome()

        self.scheduler = TaskScheduler(checkIntervalMs=60_000)
        self.scheduler.taskExecuted.connect(self._onAutomationTaskExecuted)
        self.scheduler.start()

    # =====================================================================
    # SETUP — monta cada parte da tela, chamado uma vez só na inicialização
    # =====================================================================

    def _setupScrollLayouts(self):
        # pega os layouts já criados no ‘Designer’ para poder inserir as rows dinamicamente depois
        self.scrollLayoutTasks = cast(QVBoxLayout, self.ui.scrollAreaWidgetContents.layout())
        self.scrollLayoutSystems = cast(QVBoxLayout, self.ui.scrollAreaWidgetContentsLogins.layout())
        self.scrollLayoutTasks.addStretch()
        self.scrollLayoutSystems.addStretch()

        self.featureButtons = FeatureButtons()

    def _setupClock(self):
        # ícone do bloco de data (com suavização de píxel) e relógio atualizando a cada segundo
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
        self.ui.configurations.clicked.connect(self.onOpenConfig)
        self.ui.homeButtonConfig.clicked.connect(self.goToHome)
        self.ui.homeButtonConfigSched.clicked.connect(self.goToHome)
        self.ui.homeButtonRegisterCompany.clicked.connect(self.goToHome)

        # deixa clique atravessar os títulos das tarefas, senão eles bloqueiam o clique do botão em baixo
        self.ui.buttonTitleDAS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleEFDCont.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleICMS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleNotas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setupSystemsList(self):
        # lista de ‘checkbox’ dos sistemas de NF, usada na tela de cadastro de empresa
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

        # começa vazio/desabilitado, só é populado quando escolhe uma empresa + "Consulta de Notas Fiscais"
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

        # esses dois são da tela de Configurações, mas ficam junto porque usam a mesma classe de validação
        self.ui.boxCompany.currentIndexChanged.connect(self.onConfigCompanySelected)
        self.ui.boxService.currentIndexChanged.connect(self._updateServiceDataDisplay)

    def _setupScheduling(self):
        self.ui.boxCompanyScheduling.currentIndexChanged.connect(self.onCompanySelected)
        self.ui.createButtonSchedule.clicked.connect(self.onCreateTaskClicked)
        self.ui.cancelButtonSchedule.clicked.connect(self.cancelScheduling)
        self.ui.updateListSched.clicked.connect(self.reloadTasksForSelectedCompany)

        # não deixa agendar tarefa para data que já passou
        self.ui.startScheduleDate.setMinimumDate(QDate.currentDate())

    def _setupSystemTray(self):
        self.trayIcon = QSystemTrayIcon(QIcon(resourcePath("images/icone-Impactus-semfundo.png")), self)
        self.trayIcon.setToolTip("Automação Fiscal")

        trayMenu = QMenu()

        actionOpen = trayMenu.addAction("Abrir")
        actionOpen.triggered.connect(self._restoreFromTray)

        trayMenu.addSeparator()

        actionQuit = trayMenu.addAction("Fechar programa")
        actionQuit.triggered.connect(self._quitApplication)

        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.activated.connect(self._onTrayIconActivated)

        self.trayIcon.show()

    # ==================================================================
    # NAVEGAÇÃO
    # ==================================================================

    def goToRegisterCompany(self):
        self.navigator.openPage(self.ui.pageRegisterCompany)

    def goToScheduling(self):
        self.navigator.openPage(self.ui.pageScheduling)

    def goToConfig(self):
        self.navigator.openPage(self.ui.pageConfigurations)

    def goToHome(self):
        self.navigator.openPage(self.ui.pageHome)

    # ==================================================================
    # CADASTRO DE EMPRESA
    # ==================================================================

    def onRegisterCompanyClicked(self):
        missingData = self.companyValidator.validateRegisterCompanyData()
        if missingData:
            self.companyValidator.showWarningIncompleteData(missingData)
            return

        company = self.registerCompany.register()

        self.ui.buttonSaveCompany.setEnabled(False)
        self.ui.buttonSaveCompany.setText("Salvando...")

        # cadastro roda numa thread separada para não travar a janela
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
        # limpa tudo do formulário para deixar pronto para um novo cadastro
        self.ui.companyName.clear()
        self.ui.cnpjNumber.clear()
        self.ui.imNumber.clear()
        self.ui.pathCertificate.clear()

        for i in range(self.systemsList.count()):
            item = self.systemsList.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.featureButtons.clearSystems(self.scrollLayoutSystems)

    # ==================================================================
    # AGENDAMENTO DE TAREFAS
    # ==================================================================

    def onOpenScheduling(self):
        self.goToScheduling()
        # só busca de novo se não tiver uma busca rolando ainda
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

        # bloqueia o sinal enquanto popula, senão currentIndexChanged dispara várias vezes durante o ‘loop’
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

        # ignora o pedido se já tiver uma busca rolando, evita sobrepor threads
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

        self._currentTasksCache = tasks  # guarda para achar a task pelo ‘id’ na hora de editar

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

        # consulta de notas exige um sistema cadastrado, os outros tipos não usam nf_type
        nfType = None
        if taskType == "NF":
            registeredKeys = self._getRegisteredSystemsForCurrentCompany()
            if not registeredKeys:
                QMessageBox.warning(self, "Atenção", "Esta empresa não possui nenhum sistema de notas fiscais cadastrado.")
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
        # volta o formulário de novo agendamento para o estado inicial
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
        # retorna só os sistemas que a empresa selecionada tem ‘login’ e senha preenchidos
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
        # repopula o boxNfType conforme os sistemas cadastrados da empresa atual
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

    # ==================================================================
    # EDITAR / EXCLUIR TAREFA
    # ==================================================================

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

    # ==================================================================
    # PÁGINA DE CONFIGURAÇÕES
    # ==================================================================

    def onOpenConfig(self):
        self.goToConfig()
        if self.loadCompaniesConfigWorker is None or not self.loadCompaniesConfigWorker.isRunning():
            self.loadCompaniesForConfig()

    def loadCompaniesForConfig(self):
        self.ui.boxCompany.setEnabled(False)
        self.loadCompaniesConfigWorker = LoadCompaniesWorker()
        self.loadCompaniesConfigWorker.finished.connect(self.onCompaniesLoadedForConfig)
        self.loadCompaniesConfigWorker.start()

    def onCompaniesLoadedForConfig(self, success: bool, companies: list, errorMessage: str):
        self.ui.boxCompany.setEnabled(True)

        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar as empresas.\n\n{errorMessage}")
            return

        self.loadedCompaniesConfig = companies

        self.ui.boxCompany.blockSignals(True)
        self.ui.boxCompany.clear()
        for company in companies:
            self.ui.boxCompany.addItem(company["name"], userData=company["id"])
        self.ui.boxCompany.blockSignals(False)

        if companies:
            self.onConfigCompanySelected(0)

    def onConfigCompanySelected(self, index: int):
        if index < 0 or index >= len(self.loadedCompaniesConfig):
            return

        company = self.loadedCompaniesConfig[index]

        self.ui.dataCNPJ.setText(company.get("cnpj", ""))
        self.ui.dataRS.setText(company.get("name", ""))

        self._populateServicesForCompany(company)

    def _populateServicesForCompany(self, company: dict):
        # monta o combo de serviços: os fixos do sistema (certificado) + os que a empresa
        # tem cadastrado de verdade + o item de adicionar novo serviço no final
        self.ui.boxService.blockSignals(True)
        self.ui.boxService.clear()

        self.ui.boxService.addItems(list(CONFIG_SERVICE_OPTIONS.keys()))

        systemLogins = company.get("system_logins", [])
        registeredSystemKeys = {
            login["system_name"] for login in systemLogins
            if login.get("login") and login.get("password")
        }

        for key in registeredSystemKeys:
            displayName = SYSTEM_KEY_TO_DISPLAY_NAME.get(key)
            if displayName:
                label = f"Consulta de Notas Fiscais ({displayName})"
                loginData = next((l for l in systemLogins if l["system_name"] == key), None)
                self.ui.boxService.addItem(label, userData=loginData)

        self.ui.boxService.addItem(ADD_SERVICE_OPTION_TEXT)

        self.ui.boxService.blockSignals(False)
        self._updateServiceDataDisplay()

    def _updateServiceDataDisplay(self):
        serviceText = self.ui.boxService.currentText()

        # escolheu "adicionar serviço", abre o modal em vez de mostrar dado
        if serviceText == ADD_SERVICE_OPTION_TEXT:
            self._openAddServiceDialog()
            return

        index = self.ui.boxService.currentIndex()
        if index < 0:
            return

        companyIndex = self.ui.boxCompany.currentIndex()
        if companyIndex < 0 or companyIndex >= len(self.loadedCompaniesConfig):
            return

        company = self.loadedCompaniesConfig[companyIndex]

        if serviceText in CONFIG_SERVICE_OPTIONS:
            # DAS/EFDs assinam com certificado digital, não tem usuário/senha
            self.ui.titleCompanyServiceUser.setText(
                '<html><head/><body><p><span style=" color:#042e67;">Certificado</span></p></body></html>'
            )
            certPath = company.get("certificate_path", "")
            certFileName = certPath.split("/")[-1].split("\\")[-1] if certPath else "Não cadastrado"
            self.ui.dataCompanyServiceUser.setText(certFileName)

            self.ui.companyServicePass.setVisible(False)
        else:
            # sistema de consulta de NF, mostra ‘login’ e senha
            loginData = self.ui.boxService.currentData()

            self.ui.titleCompanyServiceUser.setText(
                '<html><head/><body><p><span style=" color:#042e67;">Usuário</span></p></body></html>'
            )
            self.ui.dataCompanyServiceUser.setText(loginData.get("login", "") if loginData else "")

            self.ui.companyServicePass.setVisible(True)
            self.ui.dataCompanyServicePass.setText(loginData.get("password", "") if loginData else "")

    def _openAddServiceDialog(self):
        companyIndex = self.ui.boxCompany.currentIndex()
        if companyIndex < 0 or companyIndex >= len(self.loadedCompaniesConfig):
            return

        company = self.loadedCompaniesConfig[companyIndex]
        systemLogins = company.get("system_logins", [])
        registeredKeys = {
            login["system_name"] for login in systemLogins
            if login.get("login") and login.get("password")
        }

        # só oferece os sistemas que a empresa ainda não tem
        allSystemKeys = set(SYSTEM_KEY_TO_DISPLAY_NAME.keys())
        availableKeys = list(allSystemKeys - registeredKeys)

        dialog = AddServiceDialog(availableKeys, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_data:
            companyId = company["id"]
            data = dialog.result_data

            self.addSystemLoginWorker = AddSystemLoginWorker(
                companyId, data["system_name"], data["login"], data["password"]
            )
            self.addSystemLoginWorker.finished.connect(self.onSystemLoginAdded)
            self.addSystemLoginWorker.start()
        else:
            # cancelou o modal, volta o combo para não ficar preso no item de "adicionar"
            self.ui.boxService.setCurrentIndex(0)

    def onSystemLoginAdded(self, success: bool, errorMessage: str):
        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível adicionar o serviço.\n\n{errorMessage}")
            self.ui.boxService.setCurrentIndex(0)
            return

        QMessageBox.information(self, "Sucesso", "Serviço adicionado com sucesso!")
        self.loadCompaniesForConfig()  # recarrega tudo para já mostrar o serviço novo

    # ==================================================================
    # JANELA DE SEGUNDO PLANO / EVENTO DE FECHAR
    # ==================================================================

    def _onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restoreFromTray()

    def _restoreFromTray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.trayIcon.showMessage(
            "Automação Fiscal",
            "O programa continua rodando em segundo plano.",
            QSystemTrayIcon.MessageIcon.Information, 2000
        )

    def _quitApplication(self):
        self.trayIcon.hide()
        QApplication.quit()

    # ==================================================================
    # AUTOMAÇÃO
    # ==================================================================

    def _onAutomationTaskExecuted(self, taskData: dict, success: bool, message: str):
        if success:
            self.trayIcon.showMessage("Automação Fiscal", f"Tarefa concluída: {message}",
                                      QSystemTrayIcon.MessageIcon.Information, 3000)
        else:
            self.trayIcon.showMessage("Automação Fiscal", f"Falha na tarefa: {message}",
                                      QSystemTrayIcon.MessageIcon.Warning, 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())