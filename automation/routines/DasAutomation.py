from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from automation.AutomationTask import AutomationTask, AutomationResult
from automation.AutomationContext import AutomationContext, AutomationCancelledError
from automation.windows.CertificateSelector import selectWindowsCertificate, CertificateSelectionError

# ⚠️ ROTINA DESATIVADA — não usar/registrar no dispatcher.
#
# A Receita Federal (gov.br/e-CAC) tem detecção anti-bot agressiva
# (fingerprinting de browser, comportamento de mouse/teclado, timing
# entre ações) que identifica e bloqueia o acesso automatizado via
# Playwright, mesmo com janela anônima e Chrome real.
#
# Tentativas feitas: contexto anônimo por execução, Chrome real (não
# Chromium headless), seleção de certificado via pywinauto, pausa manual
# pra captcha. Mesmo assim o site bloqueia a automação antes de completar
# o login.
#
# Mantido aqui só de referência/histórico — o fluxo de DAS via e-CAC não
# é viável do jeito que está.
class DasAutomation(AutomationTask):

    LOGIN_URL = "https://cav.receita.fazenda.gov.br/autenticacao/login"

    def run(self, companyData: dict, taskData: dict, context: AutomationContext) -> AutomationResult:
        certificatePath = companyData.get("certificate_path")
        if not certificatePath:
            return AutomationResult(False, "Empresa não possui certificado digital cadastrado.")

        certificateIdentifier = companyData.get("name", "")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel="chrome", headless=False)
                pageContext = browser.new_context()
                page = pageContext.new_page()

                context.reportProgress("Abrindo portal e-CAC...")
                context.checkCancelled()
                page.goto(self.LOGIN_URL)

                context.reportProgress("Clicando em 'Entrar com gov.br'...")
                context.checkCancelled()
                page.get_by_role("button", name="Acesso Gov BR").click()

                if self._hasCaptcha(page):
                    context.reportProgress("Captcha detectado — resolva manualmente e aguarde.")
                    self._waitForManualResolution(page, context)

                context.reportProgress("Selecionando login por certificado digital...")
                context.checkCancelled()
                page.get_by_text("Certificado digital", exact=False).click()

                context.reportProgress("Selecionando certificado na janela do Windows...")
                context.checkCancelled()

                try:
                    selectWindowsCertificate(certificateIdentifier)
                except CertificateSelectionError as e:
                    return AutomationResult(False, f"Falha ao selecionar certificado: {e}")

                context.reportProgress("Aguardando carregamento do e-CAC...")
                try:
                    page.wait_for_selector("text=Simples Nacional", timeout=30_000)
                except PlaywrightTimeoutError:
                    return AutomationResult(False, "Login não confirmado — tela do e-CAC não carregou a tempo.")

                context.reportProgress("Login concluído com sucesso.")

                browser.close()

            return AutomationResult(True, "Login no e-CAC realizado com sucesso.")

        except AutomationCancelledError:
            raise
        except PlaywrightTimeoutError as e:
            return AutomationResult(False, f"Tempo esgotado ao interagir com a página: {e}")
        except Exception as e:
            return AutomationResult(False, f"Erro inesperado na automação: {e}")

    def _hasCaptcha(self, page) -> bool:
        try:
            return page.locator("text=captcha", exact=False).first.is_visible(timeout=3_000)
        except Exception:
            return False

    def _waitForManualResolution(self, page, context: AutomationContext, maxWaitSeconds: int = 300):
        import time
        elapsed = 0
        interval = 2

        while elapsed < maxWaitSeconds:
            context.checkCancelled()
            if not self._hasCaptcha(page):
                return
            time.sleep(interval)
            elapsed += interval

        raise TimeoutError("Captcha não foi resolvido dentro do tempo limite.")