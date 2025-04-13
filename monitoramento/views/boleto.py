from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from monitoramento.models.boleto import Boleto
from monitoramento.serializers.boleto import BoletoSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Monitoramento de Boletos"], summary="Gerencia os boletos")
class BoletoViewSet(viewsets.ModelViewSet):

    queryset = Boleto.objects.all()
    serializer_class = BoletoSerializer
    #permission_classes = [IsAuthenticated]
