import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QDialog, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QDate, QTimer
from typing import cast

from custom_widgets.AddServiceDialog import AddServiceDialog
from custom_widgets.ListWidgetCheck import ListWidgetCheck
from custom_widgets.RunAutomationDialog import RunAutomationDialog
from custom_widgets.TaskEditDialog import TaskEditDialog
from models.TaskMappings import BOX_SCHEDULE_TO_TASK_TYPE, SYSTEM_KEY_TO_DISPLAY_NAME, DISPLAY_NAME_TO_NF_TYPE, CONFIG_SERVICE_OPTIONS, ADD_SERVICE_OPTION_TEXT
from services.CompanyCache import CompanyCache
from services.FeatureButtons import FeatureButtons
from services.RegisterCompany import RegisterCompany
from services.SelectCertificate import SelectCertificate
from services.TaskScheduler import TaskScheduler
from services.ValidateDataRegister import DataValidator
from services.Navigator import Navigator
from workers.AddSystemLoginWorker import AddSystemLoginWorker
from workers.AutomationExecutionWorker import AutomationExecutionWorker
from workers.CreateTaskWorker import CreateTaskWorker
from workers.DeleteTaskWorker import DeleteTaskWorker
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

        # Workers guardados como atributo para não serem coletados pelo garbage collector enquanto continuam a rodar em segundo plano. O carregamento de empresas não entra mais aqui, isso agora é responsabilidade única do companyCache.
        self.registerWorker = None
        self.createTaskWorker = None
        self.loadTasksWorker = None
        self.updateTaskWorker = None
        self.deleteTaskWorker = None
        self.addSystemLoginWorker = None
        self.runAutomationWorker = None

        # cache das tasks da empresa atualmente aberta na tela de agendamento, usado só para achar a task pelo id na hora de editar (evita nova chamada à API)
        self._currentTasksCache: list[dict] = []

        # cache central de empresas (com systems e tasks), carregado uma vez ao abrir o app, todas as telas leem daqui em vez de bater na API toda hora
        self.companyCache = CompanyCache(self)
        self.companyCache.dataUpdated.connect(self._onCompanyCacheUpdated)
        self.companyCache.loadFailed.connect(self._onCompanyCacheFailed)
        self.companyCache.refresh()

        self._setupScrollLayouts()
        self._setupClock()
        self._setupNavigation()
        self._setupSystemsList()
        self._setupScheduleTypeOptions()
        self._setupCompanyRegistration()
        self._setupScheduling()
        self._setupSystemTray()

        self.goToHome()

        # motor que fica de olho no relógio e dispara as automações agendadas
        self.scheduler = TaskScheduler(checkIntervalMs=60_000)
        self.scheduler.taskExecuted.connect(self._onAutomationTaskExecuted)
        self.scheduler.start()

    # =====================================================================
    # SETUP — monta cada parte da tela, chamado uma vez só na inicialização
    # =====================================================================

    def _setupScrollLayouts(self):
        # pega os layouts já criados no Designer para poder inserir as rows dinamicamente depois
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

        # os 4 cards da home que rodam automação manualmente (fora do agendamento)
        self.ui.DASbutton.clicked.connect(lambda: self.onRunAutomationClicked("DAS", "DAS"))
        self.ui.ICMSbutton.clicked.connect(lambda: self.onRunAutomationClicked("EFD_ICMS", "EFD ICMS/IPI"))
        self.ui.EFDContbutton.clicked.connect(lambda: self.onRunAutomationClicked("EFD_CONT", "EFD Contribuições"))
        self.ui.Notasbutton.clicked.connect(
            lambda: self.onRunAutomationClicked("NF", "Consulta de Notas Fiscais", requiresSystem=True))

        # deixa clique atravessar os títulos das tarefas, senão eles bloqueiam o clique do botão em baixo
        self.ui.buttonTitleDAS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleEFDCont.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleICMS.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.ui.buttonTitleNotas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setupSystemsList(self):
        # lista de checkbox dos sistemas de NF, usada na tela de cadastro de empresa
        contentSystems = self.ui.selectSystemsContent
        layoutSystems = QVBoxLayout()
        layoutSystems.setContentsMargins(0, 9, 0, 9)
        contentSystems.setLayout(layoutSystems)

        self.systemsList = ListWidgetCheck(["Nota do Milhão", "IOB", "Memocash", "GINFES", "GISS Nova"])
        layoutSystems.addWidget(self.systemsList)

        self.systemsList.itemClicked.connect(self._onSystemItemClicked)

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

    # =====================================================================
    # CACHE DO PROGRAMA — fonte única de verdade dos dados de empresa,
    # evita ficar a bater na API toda a vez que troca de tela
    # =====================================================================

    def _onCompanyCacheUpdated(self, companies: list):
        # dispara sempre que o cache termina de (re)carregar, atualiza as duas combos que dependem da lista de empresas, em qualquer tela que esteja aberta
        self._refreshCompanyComboBoxes(companies)

    def _onCompanyCacheFailed(self, errorMessage: str):
        # por enquanto não trava nada, se a API estiver fora, o app continua a funcionar com o que já tinha em cache (ou vazio, se for o primeiro load)
        pass

    def _refreshCompanyComboBoxes(self, companies: list):
        self._populateComboWithCompanies(self.ui.boxCompanyScheduling, companies)
        self._populateComboWithCompanies(self.ui.boxCompany, companies)

    @staticmethod
    def _populateComboWithCompanies(combo, companies: list):
        # tenta manter a empresa que já estava selecionada, em vez de sempre voltar para o índice 0
        currentId = combo.currentData()

        combo.blockSignals(True)
        combo.clear()
        for company in companies:
            combo.addItem(company["name"], userData=company["id"])
        combo.blockSignals(False)

        if currentId is not None:
            index = combo.findData(currentId)
            if index >= 0:
                combo.setCurrentIndex(index)
                return

        if companies:
            combo.setCurrentIndex(0)

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

        self._syncGinfesLoginWithIM()

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

        if not success:
            QMessageBox.critical(self, "Erro", f"Não foi possível cadastrar a empresa.\n\n{errorMessage}")
            return

        QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
        self.companyCache.refresh()  # empresa nova, cache precisa refletir isso
        self.goToHome()

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

    def _onSystemItemClicked(self):
        item = self.systemsList.currentItem()

        # GINFES usa a Inscrição Municipal como login por padrão
        systemLogin = self.ui.imNumber.text().strip() if item.text() == "GINFES" else ""

        self.featureButtons.onSystemToggled(item, self.scrollLayoutSystems, systemLogin, "")

    def _syncGinfesLoginWithIM(self):
        # se o usuário editou a IM depois de já ter marcado o GINFES, garante que o login da row do GINFES reflita o valor mais atual antes de salvar
        ginfesRow = self.featureButtons.systemRows.get("GINFES")
        if ginfesRow is not None:
            ginfesRow.loginField.setText(self.ui.imNumber.text().strip())

    # ==================================================================
    # AGENDAMENTO DE TAREFAS
    # ==================================================================

    def onOpenScheduling(self):
        self.goToScheduling()

        if self.companyCache.isLoaded():
            self._refreshCompanyComboBoxes(self.companyCache.getAll())
        else:
            self.companyCache.refresh()  # app acabou de abrir e o cache ainda não voltou

    def onCompanySelected(self, index: int):
        companies = self.companyCache.getAll()
        if index < 0 or index >= len(companies):
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

        self._currentTasksCache = tasks  # guarda para achar a task pelo id na hora de editar

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
                QMessageBox.warning(self, "Atenção","Esta empresa não possui nenhum sistema de notas fiscais cadastrado.")
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
        self.companyCache.refresh()  # task nova entra na empresa, cache precisa refletir
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
        # retorna só os sistemas que a empresa selecionada tem login e senha preenchidos
        companyId = self.ui.boxCompanyScheduling.currentData()
        if companyId is None:
            return []
        return self.companyCache.getRegisteredSystemKeys(companyId)

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
        self.companyCache.refresh()
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

        self.companyCache.refresh()
        self.reloadTasksForSelectedCompany()

    # ==================================================================
    # AUTOMAÇÃO MANUAL (cards da Home — DAS, EFDs, Consulta de Notas)
    # ==================================================================

    def onRunAutomationClicked(self, taskType: str, taskTitle: str, requiresSystem: bool = False):
        if self.runAutomationWorker is not None and self.runAutomationWorker.isRunning():
            QMessageBox.information(self, "Aguarde", "Já existe uma automação em execução.")
            return

        companies = self.companyCache.getAll()
        if not companies:
            QMessageBox.warning(self, "Atenção", "Nenhuma empresa cadastrada ainda.")
            return

        dialog = RunAutomationDialog(taskType, taskTitle, companies, requiresSystem=requiresSystem, parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.selectedCompanyId is None:
            return

        company = self.companyCache.getById(dialog.selectedCompanyId)
        if company is None:
            return

        taskData = {"task_type": taskType}
        if requiresSystem:
            taskData["nf_type"] = dialog.selectedNfType

        # roda numa thread separada — a rotina ainda não existe de verdade, mas o dispatcher já sabe responder "não implementado" sem travar a janela
        self.runAutomationWorker = AutomationExecutionWorker(
            self.scheduler.dispatcher, company, taskData
        )
        self.runAutomationWorker.finished.connect(self._onManualAutomationFinished)
        self.runAutomationWorker.start()

    def _onManualAutomationFinished(self, taskData: dict, success: bool, message: str):
        if success:
            QMessageBox.information(self, "Sucesso", message or "Automação concluída.")
        else:
            QMessageBox.warning(self, "Aviso", message or "Automação não pôde ser executada.")

    # ==================================================================
    # PÁGINA DE CONFIGURAÇÕES
    # ==================================================================

    def onOpenConfig(self):
        self.goToConfig()

        if self.companyCache.isLoaded():
            self._refreshCompanyComboBoxes(self.companyCache.getAll())
        else:
            self.companyCache.refresh()

    def onConfigCompanySelected(self, index: int):
        companies = self.companyCache.getAll()
        if index < 0 or index >= len(companies):
            return

        company = companies[index]

        self.ui.dataCNPJ.setText(company.get("cnpj", ""))
        self.ui.dataRS.setText(company.get("name", ""))

        self._populateServicesForCompany(company)

    def _populateServicesForCompany(self, company: dict):
        # monta o comboBox de serviços: os fixos do sistema (certificado) + os que a empresa tem cadastrado de verdade + o item de adicionar novo serviço no final
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

        companies = self.companyCache.getAll()
        companyIndex = self.ui.boxCompany.currentIndex()
        if companyIndex < 0 or companyIndex >= len(companies):
            return

        company = companies[companyIndex]

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
            # sistema de consulta de NF, mostra login e senha
            loginData = self.ui.boxService.currentData()

            self.ui.titleCompanyServiceUser.setText(
                '<html><head/><body><p><span style=" color:#042e67;">Usuário</span></p></body></html>'
            )
            self.ui.dataCompanyServiceUser.setText(loginData.get("login", "") if loginData else "")

            self.ui.companyServicePass.setVisible(True)
            self.ui.dataCompanyServicePass.setText(loginData.get("password", "") if loginData else "")

    def _openAddServiceDialog(self):
        companies = self.companyCache.getAll()
        companyIndex = self.ui.boxCompany.currentIndex()
        if companyIndex < 0 or companyIndex >= len(companies):
            return

        company = companies[companyIndex]
        registeredKeys = set(self.companyCache.getRegisteredSystemKeys(company["id"]))

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
        self.companyCache.refresh()  # recarrega tudo, já refletindo o novo sistema

    # ==================================================================
    # AUTOMAÇÃO AGENDADA (disparada pelo TaskScheduler, sozinha, no horário)
    # ==================================================================

    def _onAutomationTaskExecuted(self, taskData: dict, success: bool, message: str):
        if success:
            self.trayIcon.showMessage("Automação Fiscal", f"Tarefa concluída: {message}",
                                      QSystemTrayIcon.MessageIcon.Information, 3000)
        else:
            self.trayIcon.showMessage("Automação Fiscal", f"Falha na tarefa: {message}",
                                      QSystemTrayIcon.MessageIcon.Warning, 3000)

    # ==================================================================
    # JANELA DE SEGUNDO PLANO / BANDEJA DO SISTEMA
    # ==================================================================

    def _onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restoreFromTray()

    def _restoreFromTray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        # clicar no X não fecha o programa de verdade — só esconde, para continuar rodando o scheduler em segundo plano
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())