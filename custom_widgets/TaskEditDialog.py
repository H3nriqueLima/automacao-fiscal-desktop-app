from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDateEdit, QTimeEdit, QSpinBox, QPushButton, QWidget
)
from PySide6.QtCore import QDate, QTime, Qt

from models.TaskMappings import BOX_SCHEDULE_TO_TASK_TYPE, DISPLAY_NAME_TO_NF_TYPE, SYSTEM_KEY_TO_DISPLAY_NAME, \
    NF_TYPE_TO_DISPLAY_NAME


class TaskEditDialog(QDialog):

    def __init__(self, taskData: dict, registeredSystemKeys: list[str], parent: QWidget | None = None):
        super().__init__(parent)

        self.taskData = taskData
        self.result_data: dict | None = None

        self.setWindowTitle("Editar Tarefa")
        self.setFixedSize(320, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #042e67;
                font-weight: 600;
            }
            QComboBox, QDateEdit, QTimeEdit, QSpinBox {
                background-color: transparent;
                border: 1px solid #EEEEEE;
                border-radius: 5px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Tipo de tarefa
        layout.addWidget(QLabel("Tarefa"))
        self.boxTaskType = QComboBox()
        self.boxTaskType.addItems(list(BOX_SCHEDULE_TO_TASK_TYPE.keys()))
        layout.addWidget(self.boxTaskType)

        # Tipo de NF
        self.boxNfType = QComboBox()
        registeredNames = [SYSTEM_KEY_TO_DISPLAY_NAME[k] for k in registeredSystemKeys if k in SYSTEM_KEY_TO_DISPLAY_NAME]
        self.boxNfType.addItems(registeredNames if registeredNames else ["Nenhum sistema cadastrado"])
        self.boxNfType.setEnabled(bool(registeredNames))
        layout.addWidget(self.boxNfType)

        # Data
        layout.addWidget(QLabel("Início"))
        self.dateEdit = QDateEdit()
        self.dateEdit.setCalendarPopup(True)
        layout.addWidget(self.dateEdit)

        # Horário
        layout.addWidget(QLabel("Horário"))
        self.timeEdit = QTimeEdit()
        layout.addWidget(self.timeEdit)

        # Repetição
        repeatRow = QHBoxLayout()
        self.spinRepeat = QSpinBox()
        self.spinRepeat.setRange(0, 365)
        self.boxRepeatUnit = QComboBox()
        self.boxRepeatUnit.addItems(["dias", "mês"])
        repeatRow.addWidget(QLabel("A cada"))
        repeatRow.addWidget(self.spinRepeat)
        repeatRow.addWidget(self.boxRepeatUnit)
        layout.addLayout(repeatRow)

        # Botões
        buttonsRow = QHBoxLayout()
        btnCancel = QPushButton("Cancelar")
        btnCancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btnCancel.setStyleSheet("""
            background-color: transparent;
            border: 1px solid #EEEEEE;
            border-radius: 5px;
            padding: 6px;
            color: #042e67;
        """)
        btnCancel.clicked.connect(self.reject)

        btnSave = QPushButton("Salvar")
        btnSave.setCursor(Qt.CursorShape.PointingHandCursor)
        btnSave.setStyleSheet("""
            background-color: #06adc2;
            border-radius: 5px;
            padding: 6px;
            color: white;
            font-weight: 700;
        """)
        btnSave.clicked.connect(self._onSaveClicked)

        buttonsRow.addWidget(btnCancel)
        buttonsRow.addWidget(btnSave)
        layout.addLayout(buttonsRow)

        self._fillFromTaskData()

    def _fillFromTaskData(self):
        taskType = self.taskData.get("task_type", "DAS")
        for text, mapped in BOX_SCHEDULE_TO_TASK_TYPE.items():
            if mapped == taskType:
                self.boxTaskType.setCurrentText(text)
                break

        date = QDate.fromString(self.taskData.get("date", ""), "dd/MM/yyyy")
        if date.isValid():
            self.dateEdit.setDate(date)

        time = QTime.fromString(self.taskData.get("hour", ""), "HH:mm")
        if time.isValid():
            self.timeEdit.setTime(time)

        freqType = self.taskData.get("freq_type", "")
        parts = freqType.replace("A cada", "").strip().split(" ")
        if len(parts) >= 2 and parts[0].isdigit():
            self.spinRepeat.setValue(int(parts[0]))
            unit = " ".join(parts[1:])
            index = self.boxRepeatUnit.findText(unit)
            if index >= 0:
                self.boxRepeatUnit.setCurrentIndex(index)

        nfType = self.taskData.get("nf_type")
        if nfType:
            displayName = NF_TYPE_TO_DISPLAY_NAME.get(nfType)
            if displayName:
                index = self.boxNfType.findText(displayName)
                if index >= 0:
                    self.boxNfType.setCurrentIndex(index)

    def _onSaveClicked(self):
        scheduleText = self.boxTaskType.currentText()
        taskType = BOX_SCHEDULE_TO_TASK_TYPE.get(scheduleText, "DAS")

        nfType = None
        if taskType == "NF":
            if not self.boxNfType.isEnabled():
                return
            nfType = DISPLAY_NAME_TO_NF_TYPE.get(self.boxNfType.currentText())

        self.result_data = {
            "task_type": taskType,
            "freq_type": f"A cada {self.spinRepeat.value()} {self.boxRepeatUnit.currentText()}",
            "freq_info": f"Todo dia {self.dateEdit.date().day()}",
            "date": self.dateEdit.date().toString("dd/MM/yyyy"),
            "hour": self.timeEdit.time().toString("HH:mm"),
            "nf_type": nfType,
        }
        self.accept()