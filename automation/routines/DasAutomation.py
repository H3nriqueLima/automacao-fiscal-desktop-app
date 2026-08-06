from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from automation.AutomationContext import AutomationContext, AutomationCancelledError
from automation.AutomationTask import AutomationTask, AutomationResult


class DasAutomation(AutomationTask):
    LOGIN_URL = "https://cav.receita.fazenda.gov.br/autenticacao/login"

    def run(self, companyData: dict, taskData: dict, context: AutomationContext) -> AutomationResult:
        certificatePath = companyData.get("certificate_path")
        if not certificatePath:
            return AutomationResult(False, "Empresa não possui certificado digital cadastrado.")

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
                page.get_by_alt_text("Acesso Gov BR").click()
                # page.get_by_text("Entrar com gov.br").click()

                context.reportProgress("Aguardando ação manual (captcha/certificado)...")

                browser.close()

            return AutomationResult(True, "Login iniciado (fluxo do DAS ainda incompleto).")

        except AutomationCancelledError:
            raise
        except PlaywrightTimeoutError as e:
            return AutomationResult(False, f"Tempo esgotado ao interagir com a página: {e}")
        except Exception as e:
            return AutomationResult(False, f"Erro inesperado na automação: {e}")