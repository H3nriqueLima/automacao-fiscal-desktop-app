# ==========================================================================
# TASKS FIXAS (DAS, EFD ICMS, EFD Contribuições) — título e ícone pra exibir
# ==========================================================================

TASK_TYPE_DISPLAY = {
    "DAS": ("DAS", "images/icone-DAS-semfundo.png"),
    "EFD_CONT": ("EFD Contribuições", "images/icone-EFDContr-semfundo.png"),
    "EFD_ICMS": ("EFD ICMS/IPI", "images/icone-EFDICMS-semfundo.png"),
}

# texto do combobox (boxSchedule) -> task_type salvo no banco
BOX_SCHEDULE_TO_TASK_TYPE = {
    "DAS (PGDAS-D e-CAC)": "DAS",
    "EFD ICMS/IPI": "EFD_ICMS",
    "EFD Contribuições": "EFD_CONT",
    "Consulta de Notas Fiscais": "NF",
}

# essas tasks assinam com certificado digital, não pedem usuário/senha
CERTIFICATE_BASED_TASK_TYPES = {"DAS", "EFD_ICMS", "EFD_CONT"}


# ==========================================================================
# SISTEMAS DE NOTA FISCAL — registro central de todos os sistemas suportados.
# Para adicionar um sistema novo, só mexe aqui (nos dois dicionários abaixo)
# e na lista fixa do checklist em _setupSystemsList do MainWindow.
# ==========================================================================

# chave salva no banco (system_name, minúsculo/underscore) -> nome de exibição
SYSTEM_KEY_TO_DISPLAY_NAME = {
    "ginfes": "GINFES",
    "giss_nova": "GISS Nova",
    "iob": "IOB",
    "memocash": "Memocash",
    "nota_milhao": "Nota do Milhão",
    "sieg": "SIEG",
    "bling": "Bling",
    "caixa_azul": "Caixa Azul",
    "omie": "Omie",
}

# derivado automaticamente, nunca precisa de mexer na mão
DISPLAY_NAME_TO_SYSTEM_KEY = {v: k for k, v in SYSTEM_KEY_TO_DISPLAY_NAME.items()}

# nome de exibição -> nf_type salvo no campo task_type "NF" das tasks
DISPLAY_NAME_TO_NF_TYPE = {
    "GINFES": "GINFES",
    "GISS Nova": "GISS_NOVA",
    "IOB": "IOB",
    "Memocash": "MEMOCASH",
    "Nota do Milhão": "NOTA_MILHAO",
    "SIEG": "SIEG",
    "Bling": "BLING",
    "Caixa Azul": "CAIXA_AZUL",
    "Omie": "OMIE",
}

# derivado automaticamente, nunca precisa de mexer na mão
NF_TYPE_TO_DISPLAY_NAME = {v: k for k, v in DISPLAY_NAME_TO_NF_TYPE.items()}

# título completo, usado nos cards/dialogs que mostram o nome inteiro da tarefa
NF_TYPE_DISPLAY = {
    "GINFES": "Consulta de Notas Fiscais (GINFES)",
    "GISS_NOVA": "Consulta de Notas Fiscais (GISS Nova)",
    "IOB": "Consulta de Notas Fiscais (IOB)",
    "MEMOCASH": "Consulta de Notas Fiscais (Memocash)",
    "NOTA_MILHAO": "Consulta de Notas Fiscais (Nota do Milhão)",
    "SIEG": "Consulta de Notas Fiscais (SIEG)",
    "BLING": "Consulta de Notas Fiscais (Bling)",
    "CAIXA_AZUL": "Consulta de Notas Fiscais (Caixa Azul)",
    "OMIE": "Consulta de Notas Fiscais (Omie)",
    "GENERIC": "Consulta de Notas Fiscais (Genéricas)",
}

# sistemas que usam certificado digital em vez de usuário/senha no cadastro
CERTIFICATE_BASED_SYSTEM_KEYS = {"nota_milhao"}


# ==========================================================================
# TELA DE CONFIGURAÇÕES — combobox de serviços da empresa
# ==========================================================================

CONFIG_SERVICE_OPTIONS = {
    "DAS (PGDAS-D e-CAC)": "DAS",
    "EFD ICMS/IPI": "EFD_ICMS",
    "EFD Contribuições": "EFD_CONT",
}

ADD_SERVICE_OPTION_TEXT = "+ Adicionar serviço..."