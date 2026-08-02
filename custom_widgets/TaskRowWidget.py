from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QWidget
from PySide6.QtCore import Qt, Signal

from utils.resourcePath import resourcePath


class TaskRowWidget(QFrame):
    editRequested = Signal(int)  # emite o taskId
    deleteRequested = Signal(int)

    def __init__(self,
                 taskId: int,
                 title:str,
                 freqType:str,
                 freqInfo:str,
                 date:str,
                 hour:str,
                 iconPath:str,
                 parent:QWidget|None=None):
        super().__init__(parent)

        self.taskId = taskId

        self.setObjectName("TaskRow")
        self.setStyleSheet("""
            #TaskRow {
	            background-color: white;
	            border: 1px solid lightgray;
	            border-radius: 8px;
	            padding: -1px;
	            margin: 2px;
	        }""")
        self.setFixedHeight(46)
        # Layout da linha
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Ícone
        icon = QLabel()
        icon.setPixmap(QPixmap(resourcePath(iconPath)).scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.setFixedWidth(35)

        # Titulo da Task
        taskNameColumn = QFrame()
        layoutTaskNameColumn = QHBoxLayout(taskNameColumn)
        taskName = QLabel(title)

        taskName.setStyleSheet("color: #182946; font-weight: 700; font-size: 8pt;")
        taskNameColumn.setFixedWidth(240)
        layoutTaskNameColumn.setContentsMargins(0,0,0,0)
        layoutTaskNameColumn.setSpacing(0)
        layoutTaskNameColumn.addWidget(icon)
        layoutTaskNameColumn.addWidget(taskName)
        layout.addWidget(taskNameColumn)

        # Frequência da Task
        taskFreqColumn = QFrame()
        layoutTaskFreqColumn = QVBoxLayout(taskFreqColumn)
        taskFreqType = QLabel(freqType)
        taskFreqInfo = QLabel(freqInfo)

        taskFreqType.setStyleSheet("color: #182946; font-weight: 700; font-size: 7pt;")
        taskFreqInfo.setStyleSheet("font-size: 7pt;")

        taskFreqColumn.setFixedWidth(60)
        layoutTaskFreqColumn.setContentsMargins(0,6,9,6)
        layoutTaskFreqColumn.setSpacing(0)
        layoutTaskFreqColumn.addWidget(taskFreqType)
        layoutTaskFreqColumn.addWidget(taskFreqInfo)
        layout.addWidget(taskFreqColumn)

        # Data/Hora (Repetição)
        taskRepeatColumn = QFrame()
        layoutTaskRepeatColumn = QVBoxLayout(taskRepeatColumn)
        taskRepeatDay = QLabel(date)
        taskRepeatHour = QLabel(hour)

        taskRepeatDay.setStyleSheet("color: #182946; font-weight: 700; font-size: 7pt;")
        taskRepeatHour.setStyleSheet("font-size: 7pt;")

        taskRepeatColumn.setFixedWidth(55)
        layoutTaskRepeatColumn.setContentsMargins(0,6,6,6)
        layoutTaskRepeatColumn.setSpacing(0)
        layoutTaskRepeatColumn.addWidget(taskRepeatDay)
        layoutTaskRepeatColumn.addWidget(taskRepeatHour)
        layout.addWidget(taskRepeatColumn)

        # Botões de ação (editar/excluir)
        taskButtonsColumn = QFrame()
        layoutTaskButtonsColumn = QHBoxLayout(taskButtonsColumn)
        taskEdit = QPushButton()
        taskDelete = QPushButton()

        taskEdit.setObjectName("TaskEdit")
        taskEdit.setIcon(QIcon(resourcePath("images/icone-Editar-semfundo.png")))
        taskEdit.setCursor(Qt.CursorShape.PointingHandCursor)
        taskEdit.setStyleSheet("""
            #TaskEdit {
                background-color: white; 
                border: 1px solid lightgray;
                border-radius: 5px; 
                width: 30px; 
                height: 30px;
            }
            #TaskEdit:hover {
                background-color: #C9C9C9;
            }
        """)
        taskEdit.clicked.connect(lambda: self.editRequested.emit(self.taskId))

        taskDelete.setObjectName("TaskDelete")
        taskDelete.setIcon(QIcon(resourcePath("images/icone-Excluir-semfundo.png")))
        taskDelete.setCursor(Qt.CursorShape.PointingHandCursor)
        taskDelete.setStyleSheet("""
            #TaskDelete {
                background-color: white; 
                border: 1px solid lightgray;
                border-radius: 5px; 
                width: 30px; 
                height: 30px;
            }
            #TaskDelete:hover {
                background-color: #C9C9C9;
            }
        """)
        taskDelete.clicked.connect(lambda: self.deleteRequested.emit(self.taskId))

        taskButtonsColumn.setFixedWidth(80)
        layoutTaskButtonsColumn.setContentsMargins(0,0,9,0)
        layoutTaskButtonsColumn.setSpacing(6)
        layoutTaskButtonsColumn.addWidget(taskEdit)
        layoutTaskButtonsColumn.addWidget(taskDelete)
        layout.addWidget(taskButtonsColumn)