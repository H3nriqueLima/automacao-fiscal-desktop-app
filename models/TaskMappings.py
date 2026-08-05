TASK_TYPE_DISPLAY = {
    "DAS": ("DAS", "images/icone-DAS-semfundo.png"),
    "EFD_CONT": ("EFD Contribuições", "images/icone-EFDContr-semfundo.png"),
    "EFD_ICMS": ("EFD ICMS/IPI", "images/icone-EFDICMS-semfundo.png"),
}

NF_TYPE_DISPLAY = {
    "GINFES": "Consulta de Notas Fiscais (GINFES)",
    "GISS_NOVA": "Consulta de Notas Fiscais (GISS Nova)",
    "IOB": "Consulta de Notas Fiscais (IOB)",
    "MEMOCASH": "Consulta de Notas Fiscais (Memocash)",
    "NOTA_MILHAO": "Consulta de Notas Fiscais (Nota do Milhão)",
    "GENERIC": "Consulta de Notas Fiscais (Genéricas)",
}

# texto do combobox (boxSchedule) -> task_type salvo no banco
BOX_SCHEDULE_TO_TASK_TYPE = {
    "DAS (PGDAS-D e-CAC)": "DAS",
    "EFD ICMS/IPI": "EFD_ICMS",
    "EFD Contribuições": "EFD_CONT",
    "Consulta de Notas Fiscais": "NF",
}

# texto do combobox de sistema (o mesmo da ListWidgetCheck) -> nf_type salvo no banco
SYSTEM_NAME_TO_NF_TYPE = {
    "GINFES": "GINFES",
    "GISS Nova": "GISS_NOVA",
    "IOB": "IOB",
    "Memocash": "MEMOCASH",
    "Nota do Milhão": "NOTA_MILHAO",
}

SYSTEM_KEY_TO_DISPLAY_NAME = {
    "ginfes": "GINFES",
    "giss_nova": "GISS Nova",
    "iob": "IOB",
    "memocash": "Memocash",
    "nota_milhao": "Nota do Milhão",
}

DISPLAY_NAME_TO_NF_TYPE = {
    "GINFES": "GINFES",
    "GISS Nova": "GISS_NOVA",
    "IOB": "IOB",
    "Memocash": "MEMOCASH",
    "Nota do Milhão": "NOTA_MILHAO",
}

NF_TYPE_TO_DISPLAY_NAME = {v: k for k, v in DISPLAY_NAME_TO_NF_TYPE.items()}

CERTIFICATE_BASED_TASK_TYPES = {"DAS", "EFD_ICMS", "EFD_CONT"}

CONFIG_SERVICE_OPTIONS = {
    "DAS (PGDAS-D e-CAC)": "DAS",
    "EFD ICMS/IPI": "EFD_ICMS",
    "EFD Contribuições": "EFD_CONT",
}

ADD_SERVICE_OPTION_TEXT = "+ Adicionar serviço..."

CERTIFICATE_BASED_SYSTEM_KEYS = {"nota_milhao"}

DISPLAY_NAME_TO_SYSTEM_KEY = {v: k for k, v in SYSTEM_KEY_TO_DISPLAY_NAME.items()}