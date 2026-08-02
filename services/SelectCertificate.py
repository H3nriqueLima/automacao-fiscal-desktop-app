from PySide6.QtWidgets import QFileDialog

from mainWindow_ui import Ui_MainWindow


class SelectCertificate:

    def __init__(self, mainWindow:Ui_MainWindow):
        self.ui = mainWindow

    def selectFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self.ui.buttonSearchPathCertificate,
            "Selecionar Arquivo",
            "",
            "Certificado Digital (*.pfx *.p12);;Todos os arquivos (*.*)"
        )

        if path:
            self.ui.pathCertificate.setText(path)