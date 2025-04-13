from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from financeiro.services.ranking import RankingService
from imoveis.models.administradora import Administradora
from drf_spectacular.utils import extend_schema


def get_mock_ranking_administradoras():
    return [
        {"name": "Administradora 1", "value": 1000},
        {"name": "Administradora 2", "value": 2500},
        {"name": "Administradora 3", "value": 3200},
        {"name": "Administradora 4", "value": 1500},
        {"name": "Administradora 5", "value": 1800},
        {"name": "Administradora 6", "value": 2200},
    ]


@extend_schema(
    tags=["Financeiro"], summary="Ranking de administradoras por valor total de boletos"
)
class FinanceiroRankingBoletosAPIView(APIView):
    """
    Obtenha o ranking de administradoras por valor total de boletos.
    """

    def get(self, request, *args, **kwargs) -> Response:
        # ranking = RankingService.get_ranking_administradoras()
        ranking = get_mock_ranking_administradoras()
        return Response(ranking, status=status.HTTP_200_OK)
