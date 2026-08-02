from dataclasses import dataclass

from models.SystemsLogins import SystemsLogins


@dataclass
class Company:
    name: str
    cnpj: str
    im: str
    certificatePath: str
    systemLogins:SystemsLogins|None