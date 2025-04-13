from rest_framework import viewsets
from imoveis.models.administradora import Administradora
from imoveis.serializers.administradora import AdministradoraSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Administradoras dos Imóveis"])
class AdministradoraViewSet(viewsets.ModelViewSet):
    """
    Gerencia as Administradoras dos Condomínios/Unidades/Imóveis
    """

    queryset = Administradora.objects.all()
    serializer_class = AdministradoraSerializer
