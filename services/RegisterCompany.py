from dataclasses import asdict

from PySide6.QtWidgets import QBoxLayout, QWidget

import requests
from custom_widgets.SystemRowWidget import SystemRowWidget
from mainWindow_ui import Ui_MainWindow
from models.Company import Company
from models.SystemsLogins import SystemsLogins, Credentials


class RegisterCompany:

    API_URL = "https://automacao-fiscal-api.onrender.com/empresas/"

    def __init__(self, mainWindow:Ui_MainWindow):
        self.ui = mainWindow

    def register(self) -> Company:
        systemsData: list[dict[str,str]] = self.__collectSystemsLogins(self.ui.scrollAreaWidgetContentsLogins.layout())
        systemsLogins: SystemsLogins = self.__buildSystemsLogins(systemsData)

        return Company(
            name=self.ui.companyName.text(),
            cnpj=self.ui.cnpjNumber.text(),
            im=self.ui.imNumber.text(),
            certificatePath=self.ui.pathCertificate.text(),
            systemLogins=systemsLogins
        )


    def sendToApi(self, company: Company) -> bool | None:
        global response
        payload = {
            "name": company.name,
            "cnpj": company.cnpj,
            "im": company.im,
            "certificate_path": company.certificatePath,
            "system_logins": self.__systemsLoginsToPayload(company.systemLogins)
        }

        try:
            response = requests.post(self.API_URL, json=payload, timeout=70)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as error:
            if response.status_code == 400:
                detail = response.json().get("detail", "Erro desconhecido")
                print(f"Erro: {error}\nDetalhamento:{detail}")
        except requests.exceptions.RequestException as error:
            print("Erro ao cadastrar empresa:", error)
            return False

    @staticmethod
    def __collectSystemsLogins(parent:QBoxLayout) -> list[dict[str,str]]:
        systemsData:list[dict[str,str]] = []

        layout = parent

        for i in range(layout.count()):
            systemItem = layout.itemAt(i)
            widget:SystemRowWidget|QWidget|None = systemItem.widget()

            if widget is None or not isinstance(widget, SystemRowWidget):
                continue

            systemsData.append({
                "systemName": widget.getSystemName(),
                "login": widget.getLogin(),
                "password": widget.getPassword()
            })

        return systemsData

    @staticmethod
    def __buildSystemsLogins(systemsData: list[dict[str,str]]) -> SystemsLogins:
        mapping: dict[str, str] = {
            "Nota do Milhão": "NOTA_MILHAO",
            "IOB": "IOB",
            "Memocash": "MEMOCASH",
            "GINFES": "GINFES",
            "GISS Nova": "GISS_NOVA",
            "SIEG": "SIEG",
            "Bling": "BLING",
            "Caixa Azul": "CAIXA_AZUL",
            "Omie": "OMIE",
        }

        logins = SystemsLogins()

        for system in systemsData:
            name = system["systemName"]

            if name in mapping:
                attribute = mapping[name]
                credentials = Credentials(
                    login=system["login"],
                    password=system["password"]
                )
                setattr(logins, attribute, credentials)

        return logins

    @staticmethod
    def __systemsLoginsToPayload(systemsLogins: SystemsLogins) -> dict:
        return {
            "ginfes": asdict(systemsLogins.GINFES),
            "iob": asdict(systemsLogins.IOB),
            "nota_milhao": asdict(systemsLogins.NOTA_MILHAO),
            "memocash": asdict(systemsLogins.MEMOCASH),
            "giss_nova": asdict(systemsLogins.GISS_NOVA),
            "sieg": asdict(systemsLogins.SIEG),
            "bling": asdict(systemsLogins.BLING),
            "caixa_azul": asdict(systemsLogins.CAIXA_AZUL),
            "omie": asdict(systemsLogins.OMIE),
        }