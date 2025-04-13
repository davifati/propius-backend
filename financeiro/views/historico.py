from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from monitoramento.models.boleto import Boleto


@extend_schema(tags=["Financeiro"], summary="Histórico de valores acumulados de boletos")
class HistoricoValorBoletoAcumuladoAPIView(APIView):

    def get(self, request, *args, **kwargs) -> Response:
        """
        Retorna o histórico mensal dos valores acumulados de boletos.
        """
        try:
            historico = (
                Boleto.objects.values_list("criado_em__year", "criado_em__month")
                .annotate(total=Sum("valor"))
                .order_by("criado_em__year", "criado_em__month")
            )

            data = [
                {"date": f"{str(mes).zfill(2)}/{str(ano)}", "balance": float(total)}
                for ano, mes, total in historico
            ]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao buscar histórico de boletos", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
