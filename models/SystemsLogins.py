from dataclasses import dataclass, field


@dataclass
class Credentials:
    login: str = ""
    password: str = ""

@dataclass
class SystemsLogins:
    GINFES: Credentials = field(default_factory=Credentials)
    IOB: Credentials = field(default_factory=Credentials)
    NOTA_MILHAO: Credentials = field(default_factory=Credentials)
    MEMOCASH: Credentials = field(default_factory=Credentials)
    GISS_NOVA: Credentials = field(default_factory=Credentials)
    SIEG: Credentials = field(default_factory=Credentials)
    BLING: Credentials = field(default_factory=Credentials)
    CAIXA_AZUL: Credentials = field(default_factory=Credentials)
    OMIE: Credentials = field(default_factory=Credentials)