from dataclasses import dataclass, field

from models.SystemsLogins import SystemsLogins
from models.Task import Task


@dataclass
class Company:
    name: str
    cnpj: str
    im: str
    certificatePath: str
    systemLogins: SystemsLogins | None
    tasks: list[Task] = field(default_factory=list)