from .administradora import AdministradoraSerializer
from .condominio import CondominioSerializer
from .unidade import UnidadeSerializer
from .ativos_locaticios import *
from .ativo_imovel import AtivoImovelSerializer

__all__ = [
    "AdministradoraSerializer",
    "CondominioSerializer",
    "UnidadeSerializer",
    "AtivoImovelSerializer",
]
