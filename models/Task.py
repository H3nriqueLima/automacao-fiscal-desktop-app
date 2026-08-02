from dataclasses import dataclass

from models.SystemType import SystemType
from models.TaskType import TaskType


@dataclass
class Task:
    taskType: TaskType
    freqType: str
    freqInfo: str
    date: str
    hour: str
    nfType: SystemType = SystemType.GENERIC