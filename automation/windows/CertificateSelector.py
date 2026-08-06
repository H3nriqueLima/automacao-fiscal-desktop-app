import time

from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError


class CertificateSelectionError(Exception):
    pass

def selectWindowsCertificate(certificateName: str, timeoutSeconds: int = 15) -> None:
    deadline = time.time() + timeoutSeconds

    window = None
    while time.time() < deadline:
        try:
            # título padrão dessa janela no Windows: "Selecionar um certificado"
            # (pode variar conforme idioma do SO — ajustar se necessário)
            window = Desktop(backend="uia").window(title_re=".*[Ss]elecionar.*certificado.*")
            if window.exists():
                break
        except ElementNotFoundError:
            pass
        time.sleep(0.5)
        window = None

    if window is None:
        raise CertificateSelectionError("Janela de seleção de certificado não apareceu a tempo.")

    window.set_focus()

    certList = window.child_window(control_type="List")
    items = certList.children(control_type="ListItem")

    matchedItem = None
    for item in items:
        if certificateName.lower() in item.window_text().lower():
            matchedItem = item
            break

    if matchedItem is None:
        raise CertificateSelectionError(
            f"Nenhum certificado encontrado contendo '{certificateName}' na lista."
        )

    matchedItem.click_input()

    # botão "OK" da janela — texto pode variar por idioma do SO
    okButton = window.child_window(title="OK", control_type="Button")
    okButton.click_input()