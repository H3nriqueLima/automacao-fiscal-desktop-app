from PySide6.QtWidgets import QMessageBox

from mainWindow_ui import Ui_MainWindow


class DataValidator:

    def __init__(self, mainWindow:Ui_MainWindow):
        self.ui = mainWindow

    def validateRegisterCompanyData(self):
        fields:dict[str,str] = {
            "Razão Social": self.ui.companyName.text().strip(),
            "Inscrição Municipal": self.ui.imNumber.text().strip(),
            "Certificado Digital": self.ui.pathCertificate.text().strip()
        }
        missingData:list[str] = [name for name, value in fields.items() if not value]

        cpnjDigits = "".join(c for c in self.ui.cnpjNumber.text() if c.isdigit())
        if len(cpnjDigits) != 14:
            missingData.insert(1, "CNPJ")

        return missingData

    def showWarningIncompleteData(self, missingData:list[str]):
        list:str = "\n".join(f"• {field}" for field in missingData)
        QMessageBox.warning(self.ui.pageRegisterCompany, "Dados Incompletos", f"Complete os seguintes campos:\n\n{list}")