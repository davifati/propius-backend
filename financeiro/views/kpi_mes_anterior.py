from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from financeiro.services.kpi import KPIService


@extend_schema(tags=["Financeiro"], summary="Consistência de capturas em relação ao mês anterior")
class MesAnteriorKPIAPIView(APIView):
    """
    Retorna métricas comparativas entre o mês anterior e o mês retrasado, incluindo volume financeiro, consistência de capturas e falhas.
    """

    def get(self, request, *args, **kwargs) -> Response:
        kpis = KPIService.calcular_kpis()
        return Response(kpis, status=status.HTTP_200_OK)
