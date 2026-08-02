from enum import Enum, auto


class TaskType(Enum):
    DAS = auto()
    EFD_ICMS = auto()
    EFD_CONT = auto()
    NF = auto()