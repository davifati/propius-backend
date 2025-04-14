from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from financeiro.services.ranking import RankingService
from imoveis.models.administradora import Administradora
from imoveis.models.unidade import Unidade
from monitoramento.models.boleto import Boleto

from drf_spectacular.utils import extend_schema


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Financeiro"],
    summary="Ranking de administradoras por valor total de boletos e quantidade",
)
class FinanceiroRankingBoletosAPIView(APIView):
    """
    Obtenha o ranking de administradoras por valor total de boletos e quantidade.
    Ranking por Administradora: O cálculo dos totais nesta API é feito para todas as administradoras, 
    somando o valor total de todos os boletos de todas as administradoras, sem discriminar o mês. 
    Ou seja, os valores totais apresentados são para todos os boletos de todas as administradoras, sem filtro de tempo.
    """

    def get(self, request, *args, **kwargs) -> Response:
        # Mapeia as unidades com suas administradoras
        unidades = Unidade.objects.select_related("condominio__administradora").exclude(
            pasta__isnull=True
        )
        pasta_to_adm = {}
        for unidade in unidades:
            if unidade.pasta:
                try:
                    pasta_int = int(unidade.pasta)
                    pasta_to_adm[pasta_int] = unidade.condominio.administradora.nome
                except ValueError:
                    continue

        # Inicializa os dicionários de ranking
        ranking_valores = {}
        ranking_quantidade = {}

        # Recupera todos os boletos
        boletos = Boleto.objects.all().values("pasta", "valor")

        for boleto in boletos:
            pasta = boleto["pasta"]
            valor = boleto["valor"]

            try:
                pasta_int = int(pasta)
                adm_nome = pasta_to_adm.get(pasta_int)

                if adm_nome:
                    # Ranking por valor
                    if adm_nome not in ranking_valores:
                        ranking_valores[adm_nome] = 0
                    ranking_valores[adm_nome] += float(valor)

                    # Ranking por quantidade
                    if adm_nome not in ranking_quantidade:
                        ranking_quantidade[adm_nome] = 0
                    ranking_quantidade[adm_nome] += 1
            except ValueError:
                continue

        # Organiza os rankings em listas
        ranking_valores = [
            {"name": nome.upper(), "value": round(valor_total, 2)}
            for nome, valor_total in ranking_valores.items()
        ]
        ranking_quantidade = [
            {"name": nome.upper(), "value": quantidade}
            for nome, quantidade in ranking_quantidade.items()
        ]

        # Ordena os rankings por valor (decrescente)
        ranking_valores.sort(key=lambda x: x["value"], reverse=True)
        ranking_quantidade.sort(key=lambda x: x["value"], reverse=True)

        # Retorna os dois rankings
        return Response(
            {
                "rankingValores": ranking_valores,
                "rankingQuantidade": ranking_quantidade,
            },
            status=status.HTTP_200_OK,
        )


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
class FinanceiroRankingBoletosAPIView_MOCK(APIView):
    """
    Obtenha o ranking de administradoras por valor total de boletos.
    """

    def get(self, request, *args, **kwargs) -> Response:
        # ranking = RankingService.get_ranking_administradoras()
        ranking = get_mock_ranking_administradoras()
        return Response(ranking, status=status.HTTP_200_OK)
